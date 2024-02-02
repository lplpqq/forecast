"""
scrap all info and put into database
"""

import asyncio
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any

from tqdm import tqdm
import aiohttp
from pydantic_extra_types.coordinate import Coordinate
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
CONCURRENT_SESSIONS_ALLOWED = 400


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
            self._cities = (await session.scalars(
                select(City).order_by(City.population.desc()))
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
        self,
        provider: Provider,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime
    ) -> list[Weather] | None:
        try:
            data = await provider.get_historical_weather(coordinate, start_date, end_date)
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
        try:
            data = await self._fetch(
                provider, city.coordinate, self._start_date, self._end_date
            )
        except RetryError:
            self.logger.info(
                f'We did our best to wait for the timeout on {provider.name} provider to go away. '
                f'But it never id so. We are skipping the provider for {city.name} city'
            )
            return

        if data is None:
            self.logger.warning(
                f'Could not get data for city {city.name} from provider {provider.name}. '
                f'We will be skipping it...'
            )
            return

        async with self._sessions_semaphore:
            async with self._db_session_factory() as session:
                for weather in data:
                    session.add(
                        WeatherJournal.from_weather_tuple(weather, city.id)
                    )

                try:
                    await session.commit()
                except exc.IntegrityError as error:
                    self.logger.error(
                        f'There seems to be some data missing when fetching for {city.name = } from {provider.name = }.'
                        f' Please investigate further, we will be skipping getting '
                        f'the city data with this provider for now. '
                        f'Here is the error:', error
                    )

    async def _collect_provider(self, provider: Provider) -> None:
        # TODO: More logs as to what the code is doing and is going to do so that the user is aware of what is being fetched.
        city_gather_tasks: list[asyncio.Task[None]] = []

        self.logger.info(f'Starting to collect {len(self._cities)} cities...')
        for city in self._cities:
            new_task = self._event_loop.create_task(
                self._collect_city(city, provider)
            )

            city_gather_tasks.append(new_task)

        await asyncio.gather(*city_gather_tasks)

    async def _run(self) -> None:
        await self._map_providers(lambda provider: self._collect_provider(provider))
