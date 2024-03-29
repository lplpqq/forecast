from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.base import Provider
from forecast.providers.models.weather import Weather

BASE_URL = 'https://archive-api.open-meteo.com/v1'


class OpenMeteo(Provider):
    def __init__(self, conn: aiohttp.BaseConnector, api_key: str | None) -> None:
        super().__init__(BASE_URL, conn, api_key)

    async def get_historical_weather(
        self,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Weather]:
        raw = await self.session.get_json(
            '/archive',
            params={
                'latitude': coordinate.latitude,
                'longitude': coordinate.longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'hourly': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'precipitation',
                    'rain',
                    'snowfall',
                    'snow_depth',
                    'surface_pressure',
                    'cloud_cover',
                    'wind_speed_10m',
                    #'wind_speed_100m',
                    'wind_direction_10m',
                    #'wind_direction_100m',
                    'wind_gusts_10m',
                    'cloud_cover',
                    'precipitation',
                    #'weather_code'
                ],
            },
        )

        hourly = raw['hourly']
        data = []
        for (
            time,
            temperature,
            pressure,
            wind_speed,
            wind_direction,
            humidity,
            clouds,
            precipitation,
            snow,
        ) in zip(
            hourly['time'],
            hourly['temperature_2m'],
            hourly['surface_pressure'],
            hourly['wind_speed_10m'],
            hourly['wind_direction_10m'],
            hourly['relative_humidity_2m'],
            hourly['cloud_cover'],
            hourly['precipitation'],
            hourly['snowfall'],
        ):
            data.append(
                Weather(
                    data_source=self.name,
                    date=datetime.strptime(time, '%Y-%m-%dT%H:%M'),
                    temperature=temperature,
                    pressure=pressure,
                    wind_speed=round(wind_speed / 3.6, 2),  # converts km/h to m/s
                    wind_direction=wind_direction,
                    humidity=humidity,
                    clouds=clouds,
                    precipitation=float(precipitation),
                    snow=int(snow * 1000),  # converts cm to mm
                    # description=''
                )
            )
        return data
