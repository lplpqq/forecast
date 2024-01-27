from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from models import Granularity
from .base import Provider


class VisualCrossing(Provider):
    def __init__(self, api_key: str, session: ClientSession):
        super(VisualCrossing, self).__init__(api_key,
                                             'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata',
                                             session)

    async def get_historical_weather(self, granularity: Granularity,
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        if granularity is Granularity.HOUR:
            aggregate_hours = 1
        elif granularity is Granularity.DAY:
            aggregate_hours = 24
        else:
            raise ValueError(...)

        return await self._get(
            f'/history',
            params={
                'aggregateHours': aggregate_hours,
                'location': f'{coordinate.latitude},{coordinate.longitude}',
                'startDateTime': start_date.isoformat(),
                'endDateTime': end_date.isoformat(),
                'contentType': 'csv',  # can be json
                'key': self.api_key,
            }
        )

