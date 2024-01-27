from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider


class Tomorrow(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Tomorrow, self).__init__('https://api.tomorrow.io/v4', conn, api_key)

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
