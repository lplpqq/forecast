from datetime import datetime
from typing import List

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.base import Provider
from forecast.providers.models import Weather

BASE_URL = 'https://api.weatherbit.io/v2.0/'


class WeatherBit(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str) -> None:
        super().__init__(BASE_URL, conn, api_key)

    async def get_historical_weather(
        self,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Weather]:
        raw = await self.session.get_json(
            '/history/hourly',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'key': self._api_key,
            },
        )

        return [
            Weather(
                data_source=self.name,
                date=datetime.strptime(weather['datetime'], '%Y-%m-%d:%H'),
                temperature=weather['temp'],
                pressure=weather['pres'],
                wind_speed=weather['wind_spd'],
                wind_direction=weather['wind_dir'],
                humidity=weather['rh'],
                clouds=weather['clouds'],
                precipitation=float(weather['precip']),
                snow=weather['snow'],
                # description=weather['weather']['description']
            )
            for weather in raw['data']
        ]
