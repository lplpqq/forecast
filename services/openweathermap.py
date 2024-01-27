from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from .base import Requestor


class OpenWeatherMap(Requestor):
    def __init__(self, api_key: str, session: ClientSession):
        super(OpenWeatherMap, self).__init__(api_key,
                                             'https://history.openweathermap.org/data/2.5',
                                             session)

    async def get_historical_weather(self, granularity: Literal['hour', 'day'],
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        print(self.api_key)
        return await self._get(
            f'/history/city',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'type': granularity,
                'start_date': int(datetime.timestamp(start_date)),
                'end_date': int(datetime.timestamp(end_date)),
                'appid': self.api_key,
            }
        )
