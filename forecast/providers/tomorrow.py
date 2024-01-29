from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
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
        # * https://docs.tomorrow.io/reference/historical
        return await self._post(
            '/historical',
            params={
                'apikey': self.api_key,
            },
            json={
                'timesteps': [f'{granularity.value}h'],
                'startTime': start_date.isoformat(),
                'endTime': end_date.isoformat(),
                'fields': [
                    'temperature',
                    'humidity',
                    'windSpeed',
                    'windDirection',
                    'windGust',
                    'pressureSurfaceLevel',
                    'precipitationAccumulation',
                    'snowAccumulation',
                    'cloudCover',
                ],
                'units': 'metric',
                'location': f'{coordinate.longitude}, {coordinate.latitude}',
            },
        )
