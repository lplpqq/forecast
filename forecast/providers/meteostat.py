from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Final, Literal, TypeAlias, TypedDict, cast

import aiofiles
import aiohttp
import numpy as np
import numpy.typing as npt
import orjson
import pandas as pd
from geopy.distance import geodesic
from pydantic_extra_types.coordinate import Coordinate
from scipy.spatial import distance

from forecast.enums import Granularity
from forecast.providers.base import Provider
from lib.fs_utils import format_path, validate_path

ROOT_CACHE_FOLDER: Final[Path] = Path('./.cache')
METEOSTAT_CACHE_FOLDER: Final[Path] = ROOT_CACHE_FOLDER.joinpath('./meteostat/')
STATIONS_CACHE_FOLDER: Final[Path] = METEOSTAT_CACHE_FOLDER.joinpath('./stations/')


class Name(TypedDict):
    en: str


class Identifiers(TypedDict):
    national: str
    wmo: str | None
    icao: str | None


class Location(TypedDict):
    latitude: float
    longitude: float
    elevation: int


class Model1(TypedDict):
    start: str
    end: str


class Hourly(TypedDict):
    start: str | None
    end: str | None


class Daily(TypedDict):
    start: str
    end: str


class Monthly(TypedDict):
    start: int
    end: int


class Normals(TypedDict):
    start: int | None
    end: int | None


class Inventory(TypedDict):
    model: Model1
    hourly: Hourly
    daily: Daily
    monthly: Monthly
    normals: Normals


class MeteostatStation(TypedDict):
    id: str
    name: Name
    country: str
    region: str
    identifiers: Identifiers
    location: Location
    timezone: str
    inventory: Inventory


MeteostatStations: TypeAlias = list[MeteostatStation]
FloatsArray: TypeAlias = npt.NDArray[np.float64]
DistanceComputeMethod: TypeAlias = Literal['euclidean', 'geodesic']


class Meteostat(Provider):
    _stations_cache_file: Path

    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None = None) -> None:
        super(Provider, self).__init__('https://bulk.meteostat.net/v2', conn, api_key)

        self._stations_cache_file = STATIONS_CACHE_FOLDER.joinpath('./list-lite.json')
        self._stations_df: None | pd.DataFrame = None
        self._stations_coordinates: None | FloatsArray = None

        self._freshly_created = not self._stations_cache_file.exists()
        validate_path(
            self._stations_cache_file,
            'file',
            autocreate=True,
            autocreate_is_recursive=True,
        )

    async def setup(self) -> None:
        # TODO: Consider storing this data, which is UNIQUE to meteostat in a separate db table not to load this file every time
        await super().setup()

        if not self._stations_cache_file.exists() or self._freshly_created:
            self.logger.info(
                f'Could not find stations list file cached at "{self._stations_cache_file}", fetching and saving'
            )

            validate_path(
                STATIONS_CACHE_FOLDER,
                'folder',
                {'readable', 'writable'},
                autocreate=True,
                autocreate_is_recursive=True,
            )

            self.logger.info('Fetching the stations list')
            decompressed_file = await self._request_file(
                '/stations/lite.json.gz', compression='gzip'
            )

            file_contents = decompressed_file.decode('utf-8')
            if len(file_contents) == 0:
                raise ValueError('Nothing got returned from the API')

            async with aiofiles.open(self._stations_cache_file, 'w+') as handle:
                await handle.write(file_contents)
        else:
            self.logger.info(
                f'Found cached stations list file, loading from "{format_path(self._stations_cache_file)}"'
            )
            async with aiofiles.open(self._stations_cache_file) as handle:
                file_contents = await handle.read()

            if len(file_contents) == 0:
                raise ValueError('Cached file is empty')

        stations = orjson.loads(file_contents)

        latitudes: list[float] = []
        longitudes: list[float] = []
        ids: list[str] = []

        for station in stations:
            ids.append(station['id'])

            location = station['location']
            latitudes.append(location['latitude'])
            longitudes.append(location['longitude'])

        self._stations_df = pd.DataFrame.from_dict(
            {
                'id': ids,
                'latitude': latitudes,
                'longitude': longitudes,
            }
        )

        self._stations_coordinates = cast(
            FloatsArray, self._stations_df[['latitude', 'longitude']].values
        )

    def _find_nearest_station(
        self,
        point: Coordinate,
        distance_compute_method: DistanceComputeMethod = 'euclidean',
    ) -> tuple[str, float]:
        if self._stations_df is None or self._stations_coordinates is None:
            raise ValueError('You need to call .setup() first to prime the data.')

        def geodesic_dinstance(a: FloatsArray, b: FloatsArray) -> float:
            return geodesic(a, b).km  # pyright: ignore

        metric = (
            'euclidean'
            if distance_compute_method == 'euclidean'
            else geodesic_dinstance
        )
        start = time.perf_counter()
        closest = distance.cdist(
            [(point.latitude, point.longitude)],
            self._stations_coordinates,
            metric=metric,
        )

        index = closest.argmin()
        distances = closest[0]
        end = time.perf_counter()

        self.logger.debug(
            f'Took: {end - start} to compute the closest point with {self._stations_coordinates.shape[0]} points'
        )

        return self._stations_df.iloc[index]['id'], cast(float, distances[index])

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        # NOTE: Maybe cache?
        nearest_station, distance = self._find_nearest_station(coordinate, 'euclidean')

        self.logger.debug(
            f'Nearest station for {coordinate} is {nearest_station} ({distance} km)'
        )

        # FIXME: Implement further https://github.com/meteostat/meteostat-python/blob/d9585d77ed35c30792763e9e6fe47a600556719a/meteostat/interface/point.py#L77
        raise NotImplementedError()
