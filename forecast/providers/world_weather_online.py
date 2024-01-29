from datetime import datetime, timedelta

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base import Provider
from forecast.providers.models import Weather


class WorldWeatherOnline(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        super(Provider, self).__init__(
            'https://api.worldweatheronline.com/premium/v1', conn, api_key
        )

    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        raw = await self._get(
            '/past-weather.ashx',
            params={
                'q': f'{coordinate.latitude},{coordinate.longitude}',
                'date': start_date.strftime('%Y-%m-%d'),
                'enddate': end_date.strftime('%Y-%m-%d'),
                'tp': granularity.value,
                'format': 'json',
                'key': self.api_key,
            },
        )

        data = []
        for day in raw['data']['weather']:
            day_time = datetime.strptime(day['date'], "%Y-%m-%d")
            snow = int(float(day["totalSnow_cm"]) * 1000)
            for hour in day['hourly']:
                data.append(Weather(
                    date=day_time + timedelta(hours=int(hour['time']) // 100),
                    temperature=float(hour["tempC"]),
                    apparent_temperature=float(hour["FeelsLikeC"]),
                    pressure=int(hour["pressure"]),
                    wind_speed=round((float(hour["windspeedKmph"]) / 3.6), 2),  # converts km/h to m/s
                    wind_gust_speed=round(float(hour["WindGustKmph"]) / 3.6, 2),  # converts km/h to m/s
                    wind_direction=int(hour["winddirDegree"]),
                    humidity=int(hour["humidity"]),
                    clouds=int(hour["cloudcover"]),
                    precipitation=float(hour["precipMM"]),
                    snow=snow
                ))

        return data
