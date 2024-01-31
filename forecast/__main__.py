import asyncio
import sys
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from itertools import islice
from typing import Protocol

import aiohttp
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.config import config
from forecast.db.connect import connect, create_engine
from forecast.logging import logger_provider
from forecast.providers import (
    OpenMeteo,
    OpenWeatherMap,
    Tomorrow,
    VisualCrossing,
    WeatherBit,
    WorldWeatherOnline,
)
from forecast.providers.base.provider import Provider
from forecast.providers.enums import Granularity
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


async def main(event_loop: asyncio.AbstractEventLoop) -> None:
    logger.info('Starting')
    start = time.perf_counter()

    engine = create_engine(config)
    session_factory = await connect(engine)

    async with aiohttp.TCPConnector() as connector:
        # * Providers init
        openmeteo = OpenMeteo(connector, config.data_sources.open_meteo.api_key)
        meteostat = Meteostat(connector, config.data_sources.meteostat.api_key)
        world_weather = WorldWeatherOnline(
            connector, config.data_sources.world_weather_online.api_key
        )

        providers: list[Provider] = [openmeteo, meteostat, world_weather]

        # * Services init
        populate_cities_service = PopulateCitiesService(connector, session_factory)

        collector_service = CollectorService(
            connector,
            session_factory,
            (datetime(2015, 1, 1), datetime(2016, 1, 1)),
            providers,
            Granularity.HOUR,
            event_loop,
        )

        services = [populate_cities_service, collector_service]

        async with orchestrate_anything(*services):
            await populate_cities_service.run()
            await collector_service.run()

        # location = Coordinate(
        #     latitude=Latitude(
        #         52.1652366,
        #     ),
        #     longitude=Longitude(20.8647919),
        # )

        # openmeteo = OpenMeteo(connector, config.data_sources.open_meteo.api_key)
        # meteostat = Meteostat(connector, config.data_sources.meteostat.api_key)
        # world_weather = WorldWeatherOnline(
        #     connector, config.data_sources.world_weather_online.api_key
        # )

        # TODO: Convert all of this mumbo-jumbo into a service
        # async with orchestrate_anything(openmeteo, meteostat, world_weather):
        #     world_weather_data = await world_weather.get_historical_weather(
        #         Granularity.HOUR,
        #         location,
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15),
        #     )

        #     meteostat_data = await meteostat.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
        #         start_date=datetime(2010, 1, 5),
        #         end_date=datetime(2024, 1, 15),
        #     )

        #     openmeteo_data = await openmeteo.get_historical_weather(
        #         Granularity.HOUR,
        #         location,
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15),
        #     )

        # weatherbit = WeatherBit(connector, config.data_sources.weather_bit.api_key)
        # weatherbit_data = await weatherbit.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        # tomorrow = Tomorrow(connector, config.data_sources.tomorrow.api_key)
        # tomorrow_data = await tomorrow.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        # openweathermap = OpenWeatherMap(connector, config.data_sources.open_weather_map.api_key)
        # openweathermap_data = await openweathermap.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        # visualcrossing = VisualCrossing(connector, config.data_sources.visual_crossing.api_key)
        # visualcrossing_data = await visualcrossing.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15),
        # )

        # for world_weather_, meteostat_, weathebit_, openmeteo_, tomorrow_, openweathermap_, visualcrossing_ in zip(
        #         world_weather_data, meteostat_data, weatherbit_data, openmeteo_data, tomorrow_data, openweathermap_data,
        #         visualcrossing_data
        # ):
        # for world_weather_, meteostat_, openmeteo_ in islice(
        #     zip(world_weather_data, meteostat_data, openmeteo_data), 5
        # ):
        #     print(world_weather_)
        #     print(meteostat_)
        #     print(openmeteo_)

        #     # print(weathebit_)
        #     # print(tomorrow_)
        #     # print(openweathermap_)
        #     # print(visualcrossing_)
        #     print()

    end = time.perf_counter()
    logger.info(f'Time taken - {end - start}')


def get_loop_factory() -> Callable[..., asyncio.AbstractEventLoop]:
    if sys.platform != 'win32':
        import uvloop

        return uvloop.new_event_loop

    return asyncio.new_event_loop


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=get_loop_factory()) as runner:
        loop = runner.get_loop()
        runner.run(main(loop))
