from datetime import datetime
from typing import Any

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.base import Provider
from forecast.providers.enums import Granularity

GRANULARITY_TO_STRING: dict[Granularity, str] = {
    Granularity.HOUR: 'hour',
    Granularity.DAY: 'day',
}

BASE_URL = 'https://history.openweathermap.org/data/2.5'


class OpenWeatherMap(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None) -> None:
        super().__init__(BASE_URL, conn, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> Any:
        granularity_string = GRANULARITY_TO_STRING[granularity]

        return await self.session.api_get(
            '/history/city',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'type': granularity_string,
                'start_date': int(datetime.timestamp(start_date)),
                'end_date': int(datetime.timestamp(end_date)),
                'appid': self.api_key,
            },
        )
