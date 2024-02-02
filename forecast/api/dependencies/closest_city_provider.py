import typing

import numpy as np
import numpy.typing as npt
from fastapi import HTTPException, Query, status
from scipy.spatial.distance import cdist

from forecast.api.dependencies import InjectedDBSesssion
from forecast.api.dependencies.cities_provider import InjectedCities
from forecast.db.models import City


class ClosestCityProvider:
    def __init__(self) -> None:
        self._cities_coordinates: npt.NDArray[np.float64] | None = None

    async def create_coordinates_and_cache(self, cities: list[City]) -> None:
        coordinates: list[tuple[float, float]] = []
        for city in cities:
            coordinates.append((city.latitude, city.longitude))

        self._cities_coordinates = np.array(coordinates)

    async def __call__(
        self,
        session: InjectedDBSesssion,
        cities: InjectedCities,
        latitude: float | None = Query(alias='lat', default=None, ge=-90, le=90),
        longitude: float | None = Query(alias='long', default=None, ge=-180, le=180),
        city: str | None = Query(default=None),
    ) -> City:
        if latitude is None and longitude is None and city is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='You have to either provider the lat and long query params or the city name as city, neither were provided',
            )

        if (latitude is None and longitude is not None) or (
            latitude is not None and longitude is None
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail='You have to provider both the latitude and longidute as lat and long query params',
            )

        if city is not None and longitude is not None and latitude is not None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Please either provide the long and lat or the city, can't be both",
            )

        if latitude is not None and longitude is not None:
            if self._cities_coordinates is None:
                await self.create_coordinates_and_cache(cities)

                # * There isn't really a way to make a typing.TypeGuard for this. Just for pyright
                if typing.TYPE_CHECKING:
                    assert self._cities_coordinates is not None

            closest = cdist(np.array([(latitude, longitude)]), self._cities_coordinates)

            city = cities[closest.argmin()]
        else:
            # FIXME: FIXME
            raise NotImplementedError()

        return city
