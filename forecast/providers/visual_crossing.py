# api docs https://www.visualcrossing.com/resources/documentation/weather-api/weather-api-documentation/
import asyncio
import itertools
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.base import Provider
from forecast.providers.models import Weather

BASE_URL = 'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services'


class VisualCrossing(Provider):
    def __init__(
        self, conn: aiohttp.BaseConnector, event_loop: AbstractEventLoop
    ) -> None:
        super().__init__(BASE_URL, conn, event_loop=event_loop)

    async def _get_historical_weather_chunk(
        self, coordinate: Coordinate, start_date: datetime, end_date: datetime
    ) -> list[Weather]:
        time_frame = (
            f'{start_date.strftime("%Y-%m-%d")}/'
            f'{min((start_date + timedelta(days=1)), end_date).strftime("%Y-%m-%d")}'
        )

        resp = await self.session.get_json(
            f'/timeline/{coordinate.latitude},{coordinate.longitude}/{time_frame}',
            params={
                'unitGroup': 'metric',
                'key': 'ZMM2U9XUSJ6UV37L4L49NQACY',
                'options': 'preview',
                'contentType': 'json',
            },
            headers={'referer': 'https://www.visualcrossing.com/'},
        )

        data = []
        for day_data in resp['days']:
            day = day_data['datetime']
            for hour_data in day_data['hours']:
                hour = hour_data['datetime']
                data.append(
                    Weather(
                        data_source=self.name,
                        date=datetime.strptime(f'{day} {hour}', '%Y-%m-%d %H:%M:%S'),
                        temperature=hour_data['temp'],
                        pressure=hour_data['pressure'],
                        wind_speed=hour_data['windspeed'],
                        wind_direction=hour_data['winddir'],
                        humidity=hour_data['humidity'],
                        clouds=hour_data['cloudcover'],
                        precipitation=hour_data['precip'],
                        snow=hour_data['snow'],
                    )
                )
        return data

    async def get_historical_weather(
        self,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Weather]:
        tasks = []
        while start_date < end_date:
            tasks.append(
                self._event_loop.create_task(
                    self._get_historical_weather_chunk(coordinate, start_date, end_date)
                )
            )
            start_date += timedelta(days=2)

        return list(itertools.chain.from_iterable(await asyncio.gather(*tasks)))
