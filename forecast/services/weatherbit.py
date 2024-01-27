from datetime import datetime
from typing import Literal, Optional

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from .base import Provider


class WeatherBit(Provider):
    def __init__(self, session: ClientSession, api_key: Optional[str] = None):
        super(WeatherBit, self).__init__('https://api.weatherbit.io/v2.0',
                                         session,
                                         api_key)

    async def get_historical_weather(self, granularity: Literal['hourly', 'daily'],
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        if granularity is Granularity.HOUR:
            granularity = 'hourly'
        elif granularity is Granularity.DAY:
            granularity = 'daily'

        return await self._get(
            f'/history/{granularity}',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                'key': self.api_key,
            }
        )
