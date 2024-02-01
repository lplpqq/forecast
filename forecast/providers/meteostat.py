# api docs https://dev.meteostat.net/api/stations/hourly.html#response

from __future__ import annotations

import asyncio
import gzip
import io
import time
from datetime import datetime
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
from forecast.providers.models import Weather
from lib.fs_utils import format_path, validate_path

ROOT_CACHE_FOLDER: Final[Path] = Path('./.cache')
METEOSTAT_CACHE_FOLDER: Final[Path] = ROOT_CACHE_FOLDER.joinpath('./meteostat/')
STATIONS_CACHE_FOLDER: Final[Path] = METEOSTAT_CACHE_FOLDER.joinpath('./stations/')

FloatsArray: TypeAlias = npt.NDArray[np.float64]

StationId = NewType('StationId', str)
CacheKey: TypeAlias = tuple[StationId, int]
CacheEntry: TypeAlias = pd.DataFrame


DEFAULT_CACHE_SIZE = 100

GRANULARITY_TO_STRING: Final[dict[Granularity, Literal['hourly', 'daily']]] = {
    Granularity.HOUR: 'hourly',
    Granularity.DAY: 'daily',
}


# https://dev.meteostat.net/api/stations/hourly.html#response
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


def parse_year_data(task_result: bytes) -> pd.DataFrame:
    df = pd.read_csv(
        io.BytesIO(task_result),
        names=DEFAULT_CSV_NAMES,
        parse_dates=['date'],
        compression='gzip',
    )

    return df


def _generate_endpoint_path(
    granularity: Granularity, station: str, year: int | None = None
) -> str:
    path = f'/{GRANULARITY_TO_STRING[granularity]}/'

    if granularity is Granularity.HOUR and year:
        path += f'{year}/'

    return f'{path}{station}.csv.gz'


BASE_URL = 'https://bulk.meteostat.net/v2'


class Meteostat(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None = None) -> None:
        super().__init__(BASE_URL, conn, api_key)

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

    async def setup(self) -> None:
        await super().setup()

        # TODO: Consider storing this data, which is UNIQUE to meteostat in a separate db table not to load this file every time
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
            content = await self.session.get_file('/stations/lite.json.gz')

            if len(content) == 0:
                raise ValueError('Nothing got returned from the API')

            with open(self._stations_cache_file, 'w+', encoding='utf-8') as file:
                content = gzip.decompress(content)
                file.write(content.decode('utf-8'))

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
            # fixme if you just call self.setup() from here there wont be any purpose of making setup method public
            raise ValueError('You need to call .setup() first to prime the data.')

        start = time.perf_counter()
        closest = distance.cdist(
            np.array([(point.latitude, point.longitude)]), self._stations_coordinates
        )
        end = time.perf_counter()

        self.logger.debug(
            f'Took: {end - start} to compute the closest point with {self._stations_coordinates.shape[0]} points'
        )

        index = closest.argmin()
        return StationId(self._stations_df.iloc[index]['id'])

    async def _fetch_compressed_data_for_year(
        self, granularity: Granularity, station_id: StationId, year: int
    ) -> bytes:
        endpoint = _generate_endpoint_path(granularity, station_id, year)
        compressed_data = await self.session.get_file(endpoint)

        return compressed_data

    async def get_for_station(
        self,
        station_id: StationId,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        fetch_tasks = []
        for year in range(start_date.year, end_date.year + 1):
            fetch_task = self._event_loop.create_task(
                self._fetch_compressed_data_for_year(Granularity.HOUR, station_id, year)
            )
            fetch_tasks.append(fetch_task)

        per_year_data = await asyncio.gather(*fetch_tasks)

        start = time.perf_counter()
        results = list(map(parse_year_data, per_year_data))
        end = time.perf_counter()

        self.logger.debug(f'Took to parse {len(results)} CSV file(s): {end - start}')

        concatenated_df = pd.concat(results)

        # * Postprocessing
        concatenated_df['apparent_temp'] = -1
        concatenated_df['clouds'] = -1
        concatenated_df['data_source'] = self.name

        concatenated_df = concatenated_df[
            [
                'data_source',
                'date',
                'temp',
                'apparent_temp',
                'pres',
                'wspd',
                'wpgt',
                'wdir',
                'rhum',
                'clouds',
                'prcp',
                'snow',
            ]
        ]

        concatenated_df['wspd'] = (concatenated_df['wspd'] / 3.6).round(
            2
        )  # converts km/h to m/s
        concatenated_df['wpgt'] = (concatenated_df['wpgt'] / 3.6).round(
            2
        )  # converts km/h to m/s

        concatenated_df.fillna(-1, inplace=True)
        return concatenated_df

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> Any:
        if granularity is not Granularity.HOUR:
            raise ValueError(f'Unsupported granularity: {granularity.name}')
        nearest_station = self._find_nearest_station(coordinate)

        self.logger.debug(
            f'Nearest station for ({coordinate.latitude}, {coordinate.longitude}) is {nearest_station}'
        )

        df = await self.get_for_station(nearest_station, start_date, end_date)

        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        df = df.loc[mask]

        return [Weather._make(tuple_) for tuple_ in df.itertuples(index=False)]

    @property
    def api_key(self) -> str | None:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url
