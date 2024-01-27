from datetime import datetime
from typing import Optional

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base import Provider


class OpenMeteo(Provider):
    def __init__(self, session: ClientSession, api_key: Optional[str] = None):
        super(OpenMeteo, self).__init__('https://archive-api.open-meteo.com/v1',
                                        session,
                                        api_key)

    async def get_historical_weather(self, granularity: Granularity,
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        if granularity is Granularity.HOUR:
            key = 'hourly'
        elif granularity is Granularity.DAY:
            key = 'daily'
        else:
            raise ValueError(...)

        return await self._get(
            f'/archive',
            params={
                'latitude': coordinate.latitude,
                'longitude': coordinate.longitude,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d"),
                key: ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "rain", "snowfall", "snow_depth", "surface_pressure", "cloud_cover", "wind_speed_10m", "wind_speed_100m", "wind_direction_10m", "wind_direction_100m", "wind_gusts_10m"]
            }
        )
