from datetime import datetime
from typing import Literal, Optional

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider


class OpenWeatherMap(Provider):
    def __init__(self, session: ClientSession, api_key: Optional[str] = None):
        super(OpenWeatherMap, self).__init__('https://history.openweathermap.org/data/2.5',
                                             session,
                                             api_key)

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
