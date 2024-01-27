from datetime import datetime
from typing import Any

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider


class VisualCrossing(Provider):
    def __init__(self, api_key: str, conn: aiohttp.TCPConnector) -> None:
        super(VisualCrossing, self).__init__(
            api_key,
            'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata',
            conn,
        )

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[Any, Any]:
        aggregate_hours = granularity.value

        return await self._get(
            '/history',
            params={
                'aggregateHours': aggregate_hours,
                'location': f'{coordinate.longitude},{coordinate.latitude}',
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'contentType': 'json',
                'key': self.api_key,
            },
        )
