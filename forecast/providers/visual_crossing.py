# api docs https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/

from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base import Provider
from forecast.providers.models import Weather
from forecast.providers.schema.visual_crossing import VisualCrossingSchema
from forecast.requestor import Requestor


class VisualCrossing(Provider):
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None) -> None:
        self._api_key = api_key
        self._base_url = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/weatherdata'

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
    ):  # -> VisualCrossingSchema:
        aggregate_hours = granularity.value

        raw = await self._requestor.get(
            '/history',
            params={
                'aggregateHours': aggregate_hours,
                'location': f'{coordinate.latitude},{coordinate.longitude}',
                'startDateTime': start_date.isoformat(),
                'endDateTime': end_date.isoformat(),
                'contentType': 'json',
                'key': self.api_key,
            },
        )

        return [
            Weather(
                date=datetime.fromtimestamp(weather['datetime']),
                temperature=weather['temp'],
                apparent_temperature=weather['feelslike'],
                pressure=weather['sealevelpressure'],  # note it's a sea level pressure
                wind_speed=weather['wspd'],
                wind_gust_speed=weather['wspd'] if weather['wgust'] is None else weather['wgust'],  # May be empty if it is not significantly higher than the wind speed
                wind_direction=weather['wdir'],
                humidity=weather['humidity'],
                clouds=weather['cloudcover'],
                precipitation=float(weather['precip']),
                snow=weather['snow'],
            )
            for weather in raw['locations'][next(iter(raw['locations']))]['values']
        ]

        # return raw
        # return VisualCrossingSchema.model_validate(raw)

    @property
    def api_key(self) -> str | None:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url
