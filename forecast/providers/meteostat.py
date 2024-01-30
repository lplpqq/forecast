from __future__ import annotations

import asyncio
import gzip
import io
import os
import time
from asyncio import Task
from datetime import datetime
from itertools import repeat
from pathlib import Path
from typing import Any, Final, Literal, NewType, TypeAlias, cast

import aiohttp
import numpy as np
import numpy.typing as npt
import orjson
import pandas as pd
from pydantic_extra_types.coordinate import Coordinate
from scipy.spatial import distance

from forecast.providers.base import Provider
from forecast.providers.enums import Granularity
from lib.caching.lru_cache import LRUCache
from lib.fs_utils import format_path, validate_path

ROOT_CACHE_FOLDER: Final[Path] = Path('./.cache')
METEOSTAT_CACHE_FOLDER: Final[Path] = ROOT_CACHE_FOLDER.joinpath('./meteostat/')
STATIONS_CACHE_FOLDER: Final[Path] = METEOSTAT_CACHE_FOLDER.joinpath('./stations/')


def years_from_range(start: datetime, end: datetime) -> list[int]:
    return list(range(start.year, end.year + 1))


FloatsArray: TypeAlias = npt.NDArray[np.float64]

StationId = NewType('StationId', str)
CacheKey: TypeAlias = tuple[StationId, int]
CacheEntry: TypeAlias = pd.DataFrame


DEFAULT_CACHE_SIZE = 100
CPU_COUNT = os.cpu_count() or 4

GRANULARITY_TO_STRING: Final[dict[Granularity, Literal['hourly', 'daily']]] = {
    Granularity.HOUR: 'hourly',
    Granularity.DAY: 'daily',
}

# CSV file contents:
# 1	    date	The date string (format: YYYY-MM-DD)	    String
# 2	    hour	The hour (UTC)	                            Integer
# 3	    temp	The air temperature in °C	                Float
# 4	    dwpt	The dew point in °C	                        Float
# 5	    rhum	The relative humidity in percent (%)	    Integer
# 6	    prcp	The one hour precipitation total in mm	    Float
# 7	    snow	The snow depth in mm	                    Integer
# 8	    wdir	The wind direction in degrees (°)	        Integer
# 9	    wspd	The average wind speed in km/h	            Float
# 10	wpgt	The peak wind gust in km/h	                Float
# 11	pres	The sea-level air pressure in hPa	        Float
# 12	tsun	The one hour sunshine total in minutes (m)	Integer
# 13	coco	The weather condition code	Integer

DEFAULT_CSV_NAMES = (
        'date',
        'hour',
        'temp',
        'dwpt',
        'rhum',
        'prcp',
        'snow',
        'wdir',
        'wspd',
        'wpgt',
        'pres',
        'tsun',
        'coco',
)


def parse_year_data(task_result: tuple[int, bytes]) -> tuple[int, pd.DataFrame]:
    index, raw_data = task_result
    decompressed = gzip.decompress(raw_data).decode('utf-8')
    io_string = io.StringIO(decompressed)

    df = pd.read_csv(io_string, names=DEFAULT_CSV_NAMES, parse_dates=['date'])

    return index, df


def _generate_endpoint_path(
        granularity: Granularity, station: str, year: int | None = None
) -> str:
    path = f'/{GRANULARITY_TO_STRING[granularity]}/'

    if granularity is Granularity.HOUR and year:
        path += f'{year}/'

    return f'{path}{station}.csv.gz'


class Meteostat(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None = None) -> None:
        super(Provider, self).__init__('https://bulk.meteostat.net/v2', conn, api_key)

        self._event_loop = asyncio.get_event_loop()

        self._stations_cache_file = STATIONS_CACHE_FOLDER.joinpath('./list-lite.json')
        self._stations_df: None | pd.DataFrame = None
        self._stations_coordinates: None | FloatsArray = None

        validate_path(
            self._stations_cache_file,
            'file',
            autocreate_self=False,
            autocreate_only_parent=True,
            autocreate_is_recursive=True,
        )

        self._hourly_cache = LRUCache[CacheKey, CacheEntry](DEFAULT_CACHE_SIZE)

    async def setup(self) -> None:
        # TODO: Consider storing this data, which is UNIQUE to meteostat in a separate db table not to load this file every time
        await super().setup()

        if self._stations_cache_file.exists():
            self.logger.info(
                f'Found cached stations list file, loading from "{format_path(self._stations_cache_file)}"'
            )

            with open(self._stations_cache_file, encoding='utf-8') as file:
                content = file.read()

            if len(content) == 0:
                raise ValueError('Cached file is empty')
        else:
            self.logger.info(
                f'Could not find stations list file cached at "{self._stations_cache_file}", fetching and saving'
            )

            validate_path(
                STATIONS_CACHE_FOLDER,
                'folder',
                {'readable', 'writable'},
                autocreate_self=True,
                autocreate_is_recursive=True,
            )

            self.logger.info('Fetching the stations list')
            decompressed_file = await self._request_file(
                '/stations/lite.json.gz', compression='gzip'
            )

            content = decompressed_file.decode('utf-8')
            if len(content) == 0:
                raise ValueError('Nothing got returned from the API')

            with open(self._stations_cache_file, 'w+', encoding='utf-8') as file:
                file.write(content)

        stations = orjson.loads(content)

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

    def _find_nearest_station(self, point: Coordinate) -> StationId:
        if self._stations_df is None or self._stations_coordinates is None:
            raise ValueError('You need to call .setup() first to prime the data.')

        start = time.perf_counter()
        closest = distance.cdist(
            np.array([(point.latitude, point.longitude)]),
            self._stations_coordinates
        )
        end = time.perf_counter()

        self.logger.debug(
            f'Took: {end - start} to compute the closest point with {self._stations_coordinates.shape[0]} points'
        )

        index = closest.argmin()
        return StationId(self._stations_df.iloc[index]['id'])

    async def _fetch_compressed_data_for_year(
        self, granularity: Granularity, station_id: StationId, year: int, index: int
    ) -> tuple[int, bytes]:
        endpoint = _generate_endpoint_path(granularity, station_id, year)
        compressed_data = await self._request_file(endpoint, compression=None)

        return index, compressed_data

    async def get_for_station(
        self,
        station_id: StationId,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        years_range = years_from_range(start_date, end_date)

        fetch_tasks: list[Task[tuple[int, bytes]]] = []
        combined_results: list[CacheEntry] = cast(
            list[CacheEntry], list(repeat(0, len(years_range)))
        )

        for index, year in enumerate(years_range):
            cache_key: CacheKey = (station_id, year)
            maybe_entry = self._hourly_cache.get(cache_key, None)
            if maybe_entry is not None:
                combined_results[index] = maybe_entry
                continue

            fetch_task = self._event_loop.create_task(
                self._fetch_compressed_data_for_year(
                    Granularity.HOUR, station_id, year, index
                )
            )

            fetch_tasks.append(fetch_task)

        per_year_data = await asyncio.gather(*fetch_tasks)

        start = time.perf_counter()
        results_iter = map(parse_year_data, per_year_data)
        results = list(results_iter)
        end = time.perf_counter()

        self.logger.debug(
            f'Took to parse {len(results)} CSV file(s): {end - start}'
        )

        for year, (index, data) in zip(years_range, results):
            self._hourly_cache[(station_id, year)] = data
            combined_results[index] = data

        concatednated_df = pd.concat(combined_results)
        return concatednated_df

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> Any:
        if granularity is not Granularity.HOUR:
            raise ValueError(f"Unsupported granularity: {granularity.name}")
        # NOTE: Maybe cache?
        nearest_station = self._find_nearest_station(coordinate)

        self.logger.debug(
            f'Nearest station for {coordinate} is {nearest_station} ({distance} km)'
        )

        df = await self.get_for_station(
            nearest_station, start_date, end_date
        )

        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df = df.loc[mask]

        return df
