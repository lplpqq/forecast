from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from .base import Requestor


class WeatherBit(Requestor):
    def __init__(self, api_key: str, session: ClientSession):
        super(WeatherBit, self).__init__(api_key, 'https://api.weatherbit.io/v2.0', session)

    async def get_historical_weather(self, granularity: Literal['hourly', 'daily'],
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
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
