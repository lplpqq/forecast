import asyncio
from datetime import datetime

from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude
from aiohttp import ClientSession

from services import WeatherBit


async def main():
    async with ClientSession() as session:
        weatherbit = WeatherBit('3bc5d56a89f247758f55c4023ad95035', session)

        print(await weatherbit.get_historical_weather(
            'hourly',
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


asyncio.run(main())


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
