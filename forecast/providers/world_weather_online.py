from datetime import datetime
from typing import Literal

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.providers.base import Provider


class WorldWeatherOnline(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Provider, self).__init__('https://api.worldweatheronline.com/premium/v1', conn, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        raw = await self._get(
            f'/past-weather.ashx',
            params={
                'q': f'{coordinate.latitude},{coordinate.longitude}',
                'date': start_date.strftime('%Y-%m-%d'),
                'enddate': end_date.strftime('%Y-%m-%d'),
                'tp': granularity.value,
                'format': 'json',
                'key': self.api_key,
            },
        )

        return raw
