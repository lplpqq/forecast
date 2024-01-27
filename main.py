from datetime import datetime

from fastapi import FastAPI
from requests import Session
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from services import WeatherBit


with Session() as session:
    weatherbit = WeatherBit('3bc5d56a89f247758f55c4023ad95035', session)

    print(weatherbit.get_historical_weather(
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
