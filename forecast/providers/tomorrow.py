from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base import Provider
from forecast.requestor import Requestor


class Tomorrow(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        self._api_key = api_key
        self._base_url = 'https://api.tomorrow.io/v4'

        self._requestor = Requestor(
            base_url=self._base_url,
            conn=conn,
            api_key=self._api_key
        )

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        # * https://docs.tomorrow.io/reference/historical
        return await self._requestor.post(
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

    @property
    def api_key(self) -> str | None:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url
