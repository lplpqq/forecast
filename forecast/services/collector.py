"""
scrap all info and put into database
"""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime
from itertools import islice
from typing import Any

import aiohttp
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from tenacity import (
    RetryError,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
)

from forecast.db.models import City, WeatherJournal
from forecast.providers.base import Provider
from forecast.providers.models.weather import Weather
from forecast.services.base import ServiceWithDB

DEFAULT_WAIT_TIME_SECS = 10
CONCURRENT_SESSIONS_ALLOWED = 50


class CollectorService(ServiceWithDB):
    def __init__(
        self,
        connector: aiohttp.BaseConnector,
        db_session_factory: async_sessionmaker[AsyncSession],
        start_date: datetime,
        end_date: datetime,
        provider_instances: list[Provider],
        event_loop: asyncio.AbstractEventLoop,
    ) -> None:
        super().__init__(db_session_factory=db_session_factory)

        self._cities: list[City] | None = None
        self._event_loop = event_loop
        self._connector = connector

        self._start_date = start_date
        self._end_date = end_date

        self._providers = provider_instances
        self._sessions_semaphore = asyncio.Semaphore(CONCURRENT_SESSIONS_ALLOWED)

    async def _map_providers(
        self, to_apply: Callable[[Provider], Coroutine[Any, Any, Any]]
    ):
        await asyncio.gather(
            *[
                self._event_loop.create_task(to_apply(provider))
                for provider in self._providers
            ]
        )

    async def setup(self) -> None:
        setup_providers_task = self._event_loop.create_task(
            self._map_providers(lambda provider: provider.setup())
        )

        async with self._db_session_factory() as session:
            self._cities = (
                await session.scalars(select(City).order_by(City.population.desc()))
            ).all()

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
        self, provider: Provider, city: City, start_date: datetime, end_date: datetime
    ) -> list[Weather] | None:
        try:
            data = await provider.get_historical_weather(city, start_date, end_date)
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
                case 404:
                    self.logger.info(
                        f'{provider.name} got 404, skipping the gathering for this slice.. URL = {exc.request_info.url}'
                    )

                    return None
                case _:
                    raise exc

        return data

    async def _collect_city(self, city: City, provider: Provider) -> None:
        async with self._sessions_semaphore:
            # TODO: Proper checks in order to determine wheather we need to fetch data for this city. We really need do it advance, on setup. It's really not that complicated and won't be that taxing on memory to determine wheather we should just skip the city.
            async with self._db_session_factory() as session:
                # TODO: Don't perform this query on every city. Try to cache where possible or prefect all of the data in advance. This is REALLY slow and we run out of connections the sqlalchemy connection pool. The semaphore is setup for that exact reason.
                present_data_query = select(WeatherJournal.date).where(
                    WeatherJournal.city_id == city.id,
                    WeatherJournal.date >= self._start_date,
                    WeatherJournal.date <= self._end_date,
                )
                present_data_dates = set(
                    (await session.scalars(present_data_query)).all()
                )

                start_date, end_date = self._start_date, self._end_date
                if len(present_data_dates) > 0:
                    start_date = min(min(present_data_dates), self._start_date)
                    end_date = max(max(present_data_dates), self._end_date)

                try:
                    data = await self._fetch(provider, city, start_date, end_date)
                except RetryError:
                    self.logger.info(
                        f'We did our best to wait for the timeout on {provider.name = } to go away. But it never id so. We are skipping the provider for {city.name = }'
                    )
                    return

                if data is None:
                    self.logger.warning(
                        f'Could not get data for {city.name = } from provider {provider.name = }. We will be skipping it...'
                    )
                    return

                for weather in data:
                    if weather.date in present_data_dates:
                        continue

                    session.add(WeatherJournal.from_weather_tuple(weather, city.id))

                try:
                    await session.commit()
                except exc.IntegrityError as error:
                    self.logger.error(
                        f'There seems to be some data missing when fetching for {city.name = } from {provider.name = }. Please investigate further, we will be skipping getting the city data with this provider for now. Here is the error:'
                    )
                    self.logger.error(error)

                    return

    async def _collect_provider(self, provider: Provider) -> None:
        # TODO: More logs as to what the code is doing and is going to do so that the user is aware of what is being fetched.
        city_gather_tasks: list[asyncio.Task[None]] = []

        # FIXME: Remove the slice later
        for city in islice(self._cities, 5):
            new_task = self._event_loop.create_task(self._collect_city(city, provider))

            city_gather_tasks.append(new_task)

        await asyncio.gather(*city_gather_tasks)

    async def _run(self) -> None:
        await self._map_providers(lambda provider: self._collect_provider(provider))
