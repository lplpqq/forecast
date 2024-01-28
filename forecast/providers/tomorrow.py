from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.providers.base import Provider


class Tomorrow(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Provider, self).__init__('https://api.tomorrow.io/v4', conn, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        return await self._post(
            '/historical',
            params={
                'apikey': self.api_key,
            },
            json={
                'timesteps': [f'{granularity.value}h'],
                'startTime': start_date.isoformat(),
                'endTime': end_date.isoformat(),
                'units': 'metric',
                'location': f'{coordinate.longitude}, {coordinate.latitude}',
            },
        )
