from datetime import datetime
from typing import Optional

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider


class Tomorrow(Provider):
    def __init__(self, session: ClientSession, api_key: Optional[str] = None):
        super(Tomorrow, self).__init__('https://api.tomorrow.io/v4', session, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        if granularity is Granularity.HOUR:
            aggregate_hours = 1
        elif granularity is Granularity.DAY:
            aggregate_hours = 24
        else:
            raise ValueError(...)

        return await self._post(
            '/historical',
            params={
                'apikey': self.api_key,
            },
            json={
                'timesteps': [f'{aggregate_hours}h'],
                'startTime': start_date.isoformat(),
                'endTime': end_date.isoformat(),
                'units': 'metric',
            },
        )
