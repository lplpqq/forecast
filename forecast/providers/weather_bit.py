from datetime import datetime
from typing import Literal, List

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base import Provider
from forecast.providers.models import Weather


# from forecast.providers.schema.weather_bit import WeatherBitSchema


GRANULARITY_TO_STRING: dict[Granularity, Literal['hourly', 'daily']] = {
    Granularity.HOUR: 'hourly',
    Granularity.DAY: 'hourly',
}



class WeatherBit(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Provider, self).__init__('https://api.weatherbit.io/v2.0/', conn, api_key)

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Weather]:
        granularity_string = GRANULARITY_TO_STRING[granularity]

        raw = await self._get(
            f'/history/{granularity_string}',
            params={
                'lat': coordinate.latitude,
                'lon': coordinate.longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'key': self.api_key,
            },
        )

        #print(raw)
        return [
            Weather(
                date=datetime.strptime(weather['datetime'], '%Y-%m-%d:%H'),
                temperature=weather['temp'],
                apparent_temperature=weather['app_temp'],
                pressure=weather['pres'],
                wind_speed=weather['wind_spd'],
                wind_gust_speed=weather['wind_gust_spd'],
                wind_direction=weather['wind_dir'],
                humidity=weather['rh'],
                clouds=weather['clouds'],
                precipitation=float(weather['precip']),
                snow=weather['snow'],
                #description=weather['weather']['description']
            )
            for weather in raw['data']
        ]

