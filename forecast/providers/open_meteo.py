from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base import Provider
from forecast.providers.models.weather import Weather
from forecast.requestor import Requestor


class OpenMeteo(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        self._api_key = api_key
        self._base_url = 'https://archive-api.open-meteo.com/v1'

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
        if granularity is Granularity.HOUR:
            key = 'hourly'
        elif granularity is Granularity.DAY:
            key = 'daily'
        else:
            raise ValueError(...)

        raw = await self._requestor.get(
            '/archive',
            params={
                'latitude': coordinate.latitude,
                'longitude': coordinate.longitude,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                key: [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'apparent_temperature',
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
        for time, temperature, apparent_temperature, pressure, wind_speed, wind_gust_speed, wind_direction, \
                humidity, clouds, precipitation, snow in zip(
            hourly['time'], hourly['temperature_2m'], hourly['apparent_temperature'],
            hourly['surface_pressure'],
            hourly['wind_speed_10m'], hourly['wind_gusts_10m'], hourly['wind_direction_10m'],
            hourly['relative_humidity_2m'], hourly['cloud_cover'], hourly['precipitation'],
            hourly['snowfall']
        ):
            data.append(Weather(
                date=datetime.strptime(time, "%Y-%m-%dT%H:%M"),
                temperature=temperature,
                apparent_temperature=apparent_temperature,
                pressure=pressure,
                wind_speed=round(wind_speed / 3.6, 2),  # converts km/h to m/s
                wind_gust_speed=round(wind_gust_speed / 3.6, 2),  # converts km/h to m/s
                wind_direction=wind_direction,
                humidity=humidity,
                clouds=clouds,
                precipitation=float(precipitation),
                snow=int(snow * 1000),  # converts cm to mm
                #description=''
            ))
        return data

    @property
    def api_key(self) -> str | None:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url
