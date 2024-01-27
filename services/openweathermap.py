from datetime import datetime
from typing import Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from models import Granularity
from .base import Provider


class OpenWeatherMap(Provider):
    def __init__(self, api_key: str, session: ClientSession):
        super(OpenWeatherMap, self).__init__(api_key,
                                             'https://history.openweathermap.org/data/2.5',
                                             session)

    async def get_historical_weather(self, granularity: Granularity,
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        if granularity is Granularity.HOUR:
            type_ = 'hour'
        elif granularity is Granularity.DAY:
            type_ = 'day'
        else:
            raise ValueError(...)

        return await self._get(
            f'/history/city',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'type': type_,
                'start_date': int(datetime.timestamp(start_date)),
                'end_date': int(datetime.timestamp(end_date)),
                'appid': self.api_key,
            }
        )
