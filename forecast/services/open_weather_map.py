from datetime import datetime
from typing import Any

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider

GRANULARITY_TO_STRING: dict[Granularity, str] = {
    Granularity.HOUR: 'hour',
    Granularity.DAY: 'day'
}


class OpenWeatherMap(Provider):
    def __init__(self, api_key: str, conn: aiohttp.TCPConnector) -> None:
        super(OpenWeatherMap, self).__init__(
            api_key, 'https://history.openweathermap.org/data/2.5', conn
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
