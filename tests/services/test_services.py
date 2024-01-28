from datetime import datetime

import pytest
from aiohttp.client import TCPConnector
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.enums import Granularity
from forecast.services.open_weather_map import OpenWeatherMap
from forecast.services.visual_crossing import VisualCrossing
from forecast.services.weather_bit import WeatherBit
from tests.config import config


@pytest.mark.asyncio
async def test_weatherbit(connector: TCPConnector) -> None:
    async with WeatherBit(
        connector, config.data_sources.weather_bit.api_key
    ) as weatherbit:
        print(
            await weatherbit.get_historical_weather(
                Granularity.HOUR,
                Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
                start_date=datetime(2024, 1, 5),
                end_date=datetime(2024, 1, 15),
            )
        )


@pytest.mark.asyncio
async def test_open_weather_map(connector: TCPConnector) -> None:
    async with OpenWeatherMap(
        connector,
        config.data_sources.open_weather_map.api_key,
    ) as openweathermap:
        print(
            await openweathermap.get_historical_weather(
                Granularity.HOUR,
                Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
                start_date=datetime(2024, 1, 5),
                end_date=datetime(2024, 1, 15),
            )
        )


@pytest.mark.asyncio
async def test_visaul_crossing(connector: TCPConnector) -> None:
    async with VisualCrossing(
        connector,
        config.data_sources.visual_crossing.api_key,
    ) as visualcrossing:
        print(
            await visualcrossing.get_historical_weather(
                Granularity.HOUR,
                Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
                start_date=datetime(2024, 1, 5),
                end_date=datetime(2024, 1, 15),
            )
        )
