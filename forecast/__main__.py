import asyncio
from datetime import datetime

import uvloop
from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.config import config
from forecast.logging import logger_provider
from forecast.models import Granularity
from forecast.services import WeatherBit, VisualCrossing, OpenWeatherMap


logger = logger_provider(__name__)


async def main() -> None:
    logger.info('Starting')

    async with ClientSession() as session:
        # weatherbit = WeatherBit('3bc5d56a89f247758f55c4023ad95035', session)
        #
        # print(await weatherbit.get_historical_weather(
        #     'hourly',
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

        # openweathermap = OpenWeatherMap('a20aa632a3c99a507410683fca11f82e', session)
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

        visualcrossing = VisualCrossing('RBVMRGLJV3PLQQU8WQ8AJ6LAV', session)
        print(await visualcrossing.get_historical_weather(
            Granularity.HOUR,
            Coordinate(
                latitude=Latitude(
                    35.6897
                ),
                longitude=Longitude(
                    139.6922
                )
            ),
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        ))


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
