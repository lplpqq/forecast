import asyncio
import io
import zipfile
from pathlib import Path
from typing import Final

import aiohttp
import pandas as pd
import uvloop
from aiohttp import TCPConnector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast import models
from forecast.config import config
from forecast.db.connect import connect, create_engine
from forecast.logging import logger_provider
from forecast.providers.base import Requestor
from lib.fs_utils import validate_path

logger = logger_provider(__name__)


# TODO: Abstract away...
CACHE_FOLDER: Final[Path] = Path('./.cache')
CITIES_CACHE_FILE: Final[Path] = CACHE_FOLDER.joinpath('./cities/cities.csv')

CITIES_CSV_IN_ARCHIVE_NAME = 'worldcities.csv'

# https://simplemaps.com/static/data/world-cities/basic/simplemaps_worldcities_basicv1.76.zip


async def fetch_cities(connector: aiohttp.BaseConnector) -> pd.DataFrame:
    validate_path(
        CITIES_CACHE_FILE,
        'file',
        {'readable', 'writable'},
        autocreate_only_parent=True,
        autocreate_is_recursive=True,
    )

    if CITIES_CACHE_FILE.exists():
        df = pd.read_csv(CITIES_CACHE_FILE)
        return df

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
    df = await fetch_cities(connector)

    async with session_factory() as session:
        for row in df.itertuples():
            city_tuple = models.CityTuple._make(row[1:])
            new_city = models.City.from_city_named_tuple(city_tuple)

            session.add(new_city)

        await session.commit()


async def main() -> None:
    logger.info('Starting')

    engine = create_engine(config)
    session_factory = await connect(engine)

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # async with session_factory() as session:
    #     get_hourly_weather_query = select(models.HistoricalHourlyWeather).limit(10)
    #     hourly_weather = (await session.scalars(get_hourly_weather_query)).all()
    #
    #     print(hourly_weather)

    async with TCPConnector() as connector:
        await populate_cities(connector, session_factory)

        # async with WorldWeatherOnline(connector, config.data_sources.world_weather_online.api_key) as world_weather:
        #     print(await world_weather.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(
        #             latitude=Latitude(
        #                 35.6897
        #             ),
        #             longitude=Longitude(
        #                 139.6922
        #             )
        #         ),
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15)
        #     ))

        # async with Meteostat(connector) as meteostat:
        #     print(
        #         await meteostat.get_historical_weather(
        #             Granularity.HOUR,
        #             Coordinate(
        #                 latitude=Latitude(35.6897), longitude=Longitude(139.6922)
        #             ),
        #             start_date=datetime(2010, 1, 5),
        #             end_date=datetime(2024, 1, 15),
        #         )
        #     )

        # weatherbit = WeatherBit(connector, '3bc5d56a89f247758f55c4023ad95035')
        # await weatherbit.setup()
        # print(await weatherbit.get_historical_weather(
        #     Granularity.HOUR,
        #     Coordinate(
        #         latitude=Latitude(
        #             35.6897
        #         ),
        #         longitude=Longitude(
        #             139.6922
        #         )
        #     ),
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # ))

        # async with OpenMeteo(connector) as openmeteo:
        # print(await openmeteo.get_historical_weather(
        #     Granularity.HOUR,
        #     Coordinate(
        #         latitude=Latitude(
        #             35.6897
        #         ),
        #         longitude=Longitude(
        #             on
        #         )
        #     ),
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # ))

        # async with Tomorrow(connector, config.data_sources.tomorrow.api_key) as tomorrow:
        #     print(await tomorrow.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(
        #             latitude=Latitude(
        #                 35.6897
        #             ),
        #             longitude=Longitude(
        #                 139.6922
        #             )
        #         ),
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15)
        #     ))

        # openweathermap = OpenWeatherMap(connector, config.data_sources.open_weather_map.api_key)
        # await openweathermap.setup()
        # print(await openweathermap.get_historical_weather(
        #     Granularity.HOUR,
        #     Coordinate(
        #         latitude=Latitude(
        #            35.6897
        #         ),
        #         longitude=Longitude(
        #             139.6922
        #         )
        #     ),
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # ))

        # visualcrossing = VisualCrossing(connector, config.data_sources.visual_crossing.api_key)
        # await visualcrossing.setup()
        # print(
        #     await visualcrossing.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(
        #             latitude=Latitude(
        #                 35.6897
        #             ),
        #             longitude=Longitude(
        #                 139.6922
        #             )
        #         ),
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15),
        #     )
        # )


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main())

# app = FastAPI()
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
