from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from .base import Requestor


class VisualCrossing(Requestor):
    def __init__(self, api_key: str, session: ClientSession):
        super(VisualCrossing, self).__init__(api_key,
                                             'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata',
                                             session)

    async def get_historical_weather(self, granularity: Literal['hourly', 'day'],
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        return await self._get(
            f'/history',
            params={
                'aggregateHours': 24 if granularity == 'day' else 1,
                'location': f'{coordinate.longitude},{coordinate.latitude}',
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'contentType': 'json',
                'key': self.api_key,
            }
        )
