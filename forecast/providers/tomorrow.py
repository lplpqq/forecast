from datetime import datetime
from typing import Any

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.base import Provider
from forecast.providers.enums import Granularity

BASE_URL = 'https://api.tomorrow.io/v4'


class Tomorrow(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None) -> None:
        super().__init__(BASE_URL, conn, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
        # TODO: Into common object, if we will even use it. Otherwise - delete it. We will either way have it git.
    ) -> Any:
        # * https://docs.tomorrow.io/reference/historical
        return await self.session.api_post(
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
