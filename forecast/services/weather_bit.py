from datetime import datetime
from typing import Any, Literal

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity

from .base import Provider

GRANULARITY_TO_STRING: dict[Granularity, Literal['hourly', 'daily']] = {
    Granularity.HOUR: 'hourly',
    Granularity.DAY: 'hourly',
}


class WeatherBit(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(WeatherBit, self).__init__(
            'https://api.weatherbit.io/v2.0/', conn, api_key
        )

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[Any, Any]:
        granularity_string = GRANULARITY_TO_STRING[granularity]

        return await self._get(
            f'/history/{granularity_string}',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'key': self.api_key,
            },
        )
