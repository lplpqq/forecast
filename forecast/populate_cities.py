import io
import zipfile
from pathlib import Path
from typing import Final

import aiohttp
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast import models
from forecast.providers.base import Requestor
from lib.fs_utils import validate_path

# TODO: Abstract away...
CACHE_FOLDER: Final[Path] = Path('./.cache')
CITIES_CACHE_FILE: Final[Path] = CACHE_FOLDER.joinpath('./cities/cities.csv')

CITIES_CSV_IN_ARCHIVE_NAME = 'worldcities.csv'


async def fetch_cities_list(connector: aiohttp.BaseConnector) -> pd.DataFrame:
    validate_path(
        CITIES_CACHE_FILE,
        'file',
        {'readable', 'writable'},
        autocreate_only_parent=True,
        autocreate_is_recursive=True,
    )

    # if CITIES_CACHE_FILE.exists():
    #     df = pd.read_csv(CITIES_CACHE_FILE)
    #     return df

    async with Requestor(
        'https://simplemaps.com/static/data/world-cities/basic', connector
    ) as requestor:
        archive = await requestor.get_file('/simplemaps_worldcities_basicv1.76.zip')
        file_io = io.BytesIO(archive)

        with zipfile.ZipFile(file_io) as archive_handle:
            if CITIES_CSV_IN_ARCHIVE_NAME not in archive_handle.namelist():
                raise ValueError(
                    f'The wanted file "{CITIES_CSV_IN_ARCHIVE_NAME}" is not found in the archive'
                )

            data = archive_handle.read(CITIES_CSV_IN_ARCHIVE_NAME)
            csv_file_io = io.BytesIO(data)

    df = pd.read_csv(csv_file_io)
    df = df.where(df['population'] > 1000).dropna(axis=0, how='any')

    df.to_csv(CITIES_CACHE_FILE, index=False)

    return df


async def populate_cities(
    connector: aiohttp.BaseConnector, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    df = await fetch_cities_list(connector)

    async with session_factory() as session:
        present_source_ids_query = select(models.City.source_list_id)
        present_source_ids = set(await session.scalars(present_source_ids_query))

        for row in df.itertuples():
            city_tuple = models.CityTuple._make(row[1:])
            if int(city_tuple.id) in present_source_ids:
                continue

            new_city = models.City.from_city_named_tuple(city_tuple)

            session.add(new_city)

        await session.commit()
