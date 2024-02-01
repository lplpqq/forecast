"""
scrap all info and put into database
"""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime, timedelta
from itertools import islice
from typing import Any

import aiohttp
from pydantic_extra_types.coordinate import Coordinate
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tenacity import after_log, retry, retry_if_exception_type, stop_after_attempt

from forecast.db.models import City, WeatherJournal
from forecast.providers.base import Provider
from forecast.providers.models.weather import Weather
from forecast.services.base import ServiceWithDB

DEFAULT_WAIT_TIME_SECS = 10


class CollectorService(ServiceWithDB):
    def __init__(
            self,
            connector: aiohttp.BaseConnector,
            db_session_factory: async_sessionmaker[AsyncSession],
            start_date: datetime,
            end_date: datetime,
            provider_instances: list[Provider],
            event_loop: asyncio.AbstractEventLoop
    ) -> None:
        super().__init__(db_session_factory=db_session_factory)

        self._cities: list[City] | None = None
        self._event_loop = event_loop
        self._connector = connector

        self._start_date = start_date
        self._end_date = end_date

        self._providers = provider_instances

    async def _map_providers(
            self, to_apply: Callable[[Provider], Coroutine[Any, Any, Any]]
    ):
        await asyncio.gather(*[self._event_loop.create_task(to_apply(provider))
                               for provider in self._providers])

    async def setup(self) -> None:
        setup_providers_task = self._event_loop.create_task(
            self._map_providers(lambda provider: provider.setup())
        )

        async with self._db_session_factory() as session:
            self._cities = (await session.scalars(
                select(City).order_by(City.population.desc())
            )).all()

        await setup_providers_task
        await super().setup()

    async def teardown(self) -> None:
        await self._map_providers(lambda provider: provider.teardown())

        await super().teardown()

    @retry(
        retry=(retry_if_exception_type(aiohttp.ClientResponseError)),
        stop=stop_after_attempt(3),
    )
    async def _fetch(
            self,
            provider: Provider,
            city: City,
            start_date: datetime,
            end_date: datetime
    ) -> list[Weather]:
        try:
            data = await provider.get_historical_weather(
                city, start_date, end_date
            )
        except aiohttp.ClientResponseError as exc:
            self.logger.info(
                f'Provider {provider.name} encountered an http error: {exc.status}'
            )

            # FIXME: Handle 404
            match exc.status:
                case 429:
                    self.logger.info(
                        f'{provider.name} got 429, waiting for {DEFAULT_WAIT_TIME_SECS} second(s)...'
                    )

                    await asyncio.sleep(DEFAULT_WAIT_TIME_SECS)
                    raise exc
                case _:
                    raise exc

        return data

    async def _collect_city(self, city: City, provider: Provider) -> None:
        async with self._db_session_factory() as session:
            # FIXME: include the city in the query, cause this is not the right thing.
            # present_data_range_query = select(
            #     func.min(models.HistoricalHourlyWeather.date),
            #     func.max(models.HistoricalHourlyWeather.date),
            # )

            # present_data_range = (
            #     await session.execute(present_data_range_query)
            # ).first()
            # if not (
            #     present_data_range is None
            #     or present_data_range[0] is None
            #     or present_data_range[0] is None
            # ):
            #     present_data_range = tuple(present_data_range)
            #     ranges_delta = (self._timeframe[1] - self._timeframe[0]) - (
            #         present_data_range[1] - present_data_range[0]
            #     )

            #     if ranges_delta < timedelta(days=1):
            #         self.logger.info(
            #             f'{present_data_range} == {self._timeframe}, skipping gathering for {provider.name} provider'
            #         )
            #         return

            present_data_query = select(WeatherJournal.date).where(
                 WeatherJournal.city_id == city.id,
                 WeatherJournal.date >= self._start_date,
                 WeatherJournal.date <= self._end_date,
            )
            present_data_dates = set((await session.scalars(present_data_query)).all())

            start_date, end_date = self._start_date, self._end_date
            if len(present_data_dates) > 0:
                # TODO: Consider implementing loging for splitting into multuple requests with
                #  different ranges if the gaps are small in size, even though spreadout throught
                #  a big period of time
                start_date = min(min(present_data_dates), self._start_date)
                end_date = max(max(present_data_dates), self._end_date)

            data = await self._fetch(provider, city, start_date, end_date)

            for weather in data:
                if weather.date in present_data_dates:
                    continue

                session.add(
                    WeatherJournal.from_weather_tuple(weather, city.id)
                )

            await session.commit()

    async def _collect_provider(self, provider: Provider) -> None:
        # TODO: More logs as to what the code is doing and is going to do so that the user is aware of what is being fetched.
        city_gather_tasks: list[asyncio.Task[None]] = []

        # FIXME: Remove the slice later
        for city in islice(self._cities, 100):
            new_task = self._event_loop.create_task(
                self._collect_city(city, provider)
            )

            city_gather_tasks.append(new_task)

        await asyncio.gather(*city_gather_tasks)

    async def _run(self) -> None:
        await self._map_providers(lambda provider: self._collect_provider(provider))
