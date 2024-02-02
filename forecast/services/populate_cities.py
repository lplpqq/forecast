import io
import zipfile
from pathlib import Path
from typing import Final

import aiohttp
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.db.models import City
from forecast.services.base import Service
from forecast.services.models import CityTuple
from lib.fs_utils import validate_path

CACHE_FOLDER: Final[Path] = Path('./.cache')
CITIES_CACHE_FILE: Final[Path] = CACHE_FOLDER.joinpath('./cities/cities.csv')

CITIES_CSV_IN_ARCHIVE_NAME = 'worldcities.csv'

BASE_URL = 'https://simplemaps.com/static/data/world-cities/basic'
COLUMNS = ('city', 'lat', 'lng', 'country', 'population')
MIN_POPULATION = 2_000_000


class PopulateCitiesService(Service):
    def __init__(
        self,
        db_session_factory: async_sessionmaker[AsyncSession],
        *,
        connector: aiohttp.BaseConnector,
    ) -> None:
        super().__init__(db_session_factory, connector=connector, base_url=BASE_URL)

        self._cities_df: pd.DataFrame | None = None

    async def fetch_cities_list(self) -> pd.DataFrame:
        validate_path(
            CITIES_CACHE_FILE,
            'file',
            {'readable', 'writable'},
            autocreate_only_parent=True,
            autocreate_is_recursive=True,
        )

        try:
            df = pd.read_csv(CITIES_CACHE_FILE, usecols=COLUMNS)
            return df[
                (df['population'] >= MIN_POPULATION)
                & ~(df['country'].isin(['China', 'India']))
            ]
        except FileNotFoundError:
            pass

        archive = await self._aiohttp_session.get_raw(
            '/simplemaps_worldcities_basicv1.76.zip'
        )

        with zipfile.ZipFile(io.BytesIO(archive)) as archive_handle:
            try:
                data = archive_handle.read(CITIES_CSV_IN_ARCHIVE_NAME)
            except KeyError:
                raise ValueError(
                    f'The wanted file "{CITIES_CSV_IN_ARCHIVE_NAME}" is not found in the archive'
                )

        df = pd.read_csv(io.BytesIO(data), usecols=COLUMNS)
        df['population'] = df['population'].fillna(value=0).astype(int)
        # fill None values with 0 in order to successfully cast population into integer
        df.dropna(axis=0)
        df.to_csv(CITIES_CACHE_FILE, index=False)

        return df[
            (df['population'] >= MIN_POPULATION)
            & ~(df['country'].isin(['China', 'India']))
        ]

    async def setup(self) -> None:
        await super().setup()
        self._cities_df = await self.fetch_cities_list()

    async def populate_cities(self) -> None:
        async with self._db_session_factory() as session:
            present_locations = set(
                (await session.execute(select(City.latitude, City.longitude))).all()
            )

            for row in self._cities_df.itertuples(index=False):
                city_tuple = CityTuple._make(row)
                if (city_tuple.latitude, city_tuple.longitude) in present_locations:
                    continue

                session.add(City.from_city_named_tuple(city_tuple))

            await session.commit()

    async def _run(self) -> None:
        await self.populate_cities()
