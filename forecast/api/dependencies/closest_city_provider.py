import typing

import numpy as np
import numpy.typing as npt
from fastapi import HTTPException, Query, status
from scipy.spatial.distance import cdist
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from forecast.api.dependencies import InjectedDBSesssion
from forecast.db.models import City


class ClosestCityProvider:
    def __init__(self) -> None:
        self._cities: list[City] | None = []
        self._cities_coordinates: npt.NDArray[np.float64] | None = None

    async def fetch_cities_and_cache(self, session: AsyncSession) -> None:
        self._cities = list((await session.scalars(select(City))).all())

        coordinates: list[tuple[float, float]] = []
        for city in self._cities:
            coordinates.append((city.latitude, city.longitude))

        self._cities_coordinates = np.array(coordinates)

    async def __call__(
        self,
        session: InjectedDBSesssion,
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
            if self._cities_coordinates is None or self._cities is None:
                await self.fetch_cities_and_cache(session)

                # * There isn't really a way to make a typing.TypeGuard for this. Just for pyright
                if typing.TYPE_CHECKING:
                    assert self._cities is not None
                    assert self._cities_coordinates is not None

            closest = cdist(np.array([(latitude, longitude)]), self._cities_coordinates)

            city = self._cities[closest.argmin()]
        else:
            # FIXME: FIXME
            raise NotImplementedError()

        return city
