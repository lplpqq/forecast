from datetime import datetime

import pytest
from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.services.weatherbit import WeatherBit
from tests.config import config


@pytest.mark.asyncio
async def test_weatherbit():
    async with ClientSession() as session:
        weatherbit = WeatherBit(config.data_sources.weatherbit.api_key, session)

        print(
            await weatherbit.get_historical_weather(
                'hourly',
                Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
                start_date=datetime(2024, 1, 5),
                end_date=datetime(2024, 1, 15),
            )
        )
