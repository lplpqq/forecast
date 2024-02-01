import asyncio
import sys
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Protocol

import aiohttp

from forecast.config import config
from forecast.db.connect import connect, create_engine
from forecast.logging import logger_provider
from forecast.parse_args import create_parser, parse_args
from forecast.providers import OpenMeteo, WorldWeatherOnline, VisualCrossing
from forecast.providers.meteostat import Meteostat
from forecast.services import CollectorService, PopulateCitiesService


logger = logger_provider(__name__)


class Orchestratable(Protocol):
    async def setup(self) -> None:
        ...

    async def teardown(self) -> None:
        ...


@asynccontextmanager
async def orchestrate_anything(
    *orchestratables: Orchestratable,
) -> AsyncIterator[None]:
    await asyncio.gather(
        *[orchestratable.setup() for orchestratable in orchestratables]
    )

    try:
        yield
    finally:
        await asyncio.gather(
            *[orchestratable.teardown() for orchestratable in orchestratables]
        )


async def run_gather(
    event_loop: asyncio.AbstractEventLoop, start_date: datetime, end_date: datetime
) -> None:
    logger.info('Starting')
    start = time.perf_counter()

    engine = create_engine(config)
    session_factory = await connect(engine)

    async with aiohttp.TCPConnector() as connector:
        # * Providers init
        openmeteo = OpenMeteo(connector, config.data_sources.open_meteo.api_key)
        meteostat = Meteostat(connector, event_loop=event_loop)
        world_weather = WorldWeatherOnline(connector, config.data_sources.world_weather_online.api_key)
        visual_crossing = VisualCrossing(connector, event_loop=event_loop)

        # * Services init
        populate_cities_service = PopulateCitiesService(connector, session_factory)

        collector_service = CollectorService(
            connector,
            session_factory,
            start_date,
            end_date,
            [openmeteo, meteostat, world_weather, visual_crossing],
            event_loop,
        )

        services = [populate_cities_service, collector_service]

        async with orchestrate_anything(*services):
            await populate_cities_service.run()
            await collector_service.run()

    end = time.perf_counter()
    logger.info(f'Time taken - {end - start}')


START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2016, 1, 1)


async def main(event_loop: asyncio.AbstractEventLoop) -> None:
    parser = create_parser()
    args = parse_args(parser)

    if args.initial_run:
        delta = END_DATE - START_DATE
        logger.info(
            f'Starting the gathering for {START_DATE.isoformat()} - {END_DATE.isoformat()}, a {delta = }'
        )

        await run_gather(event_loop, START_DATE, END_DATE)
    else:
        logger.info('Skipping the gather step. To gather provide --initial')


def get_loop_factory() -> Callable[..., asyncio.AbstractEventLoop]:
    if sys.platform != 'win32':
        import uvloop

        return uvloop.new_event_loop

    return asyncio.new_event_loop


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=get_loop_factory()) as runner:
        loop = runner.get_loop()
        runner.run(main(loop))
