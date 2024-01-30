import asyncio
import sys
from datetime import datetime

from aiohttp import TCPConnector
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.providers.enums import Granularity
from forecast.logging import logger_provider
from forecast.providers import WeatherBit, OpenMeteo, WorldWeatherOnline, Tomorrow, OpenWeatherMap, VisualCrossing
from forecast.providers.meteostat import Meteostat

logger = logger_provider(__name__)


async def main() -> None:
    logger.info('Starting')

    async with TCPConnector() as connector:
        location = Coordinate(
            latitude=Latitude(
                52.1652366,
            ),
            longitude=Longitude(
                20.8647919
            )
        )


        world_weather = WorldWeatherOnline(connector, "c6b25e7a6c8046db9a3133035242801")
        await world_weather.setup()
        world_weather_data = await world_weather.get_historical_weather(
            Granularity.HOUR,
            location,
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        )

        meteostat = Meteostat(connector, '3bc5d56a89f247758f55c4023ad95035')
        await meteostat.setup()
        meteostat_data = await meteostat.get_historical_weather(
            Granularity.HOUR,
            Coordinate(
                latitude=Latitude(35.6897), longitude=Longitude(139.6922)
            ),
            start_date=datetime(2010, 1, 5),
            end_date=datetime(2024, 1, 15),
        )

        # weatherbit = WeatherBit(connector, '3bc5d56a89f247758f55c4023ad95035')
        # await weatherbit.setup()
        # weatherbit_data = await weatherbit.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        openmeteo = OpenMeteo(connector)
        await openmeteo.setup()
        openmeteo_data = await openmeteo.get_historical_weather(
            Granularity.HOUR,
            location,
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        )

        # tomorrow = Tomorrow(connector, config.data_sources.tomorrow.api_key)
        # await tomorrow.setup()
        # tomorrow_data = await tomorrow.get_historical_weather(
        #     Granularity.HOUR,
        #     Coordinate(
        #         latitude=Latitude(
        #             35.6897
        #         ),
        #         longitude=Longitude(
        #             139.6922
        #         )
        #     ),
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        # openweathermap = OpenWeatherMap(connector, config.data_sources.open_weather_map.api_key)
        # await openweathermap.setup()
        # openweathermap_data = await openweathermap.get_historical_weather(
        #     Granularity.HOUR,
        #     location,
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # )

        # visualcrossing = VisualCrossing(connector, config.data_sources.visual_crossing.api_key)
        # await visualcrossing.setup()
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
        for world_weather_, meteostat_, openmeteo_ in zip(
                world_weather_data, meteostat_data, openmeteo_data
        ):
            print(world_weather_)
            print(meteostat_)
            # print(weathebit_)
            print(openmeteo_)
            # print(tomorrow_)
            # print(openweathermap_)
            # print(visualcrossing_)
            print()


def get_loop_factory() -> asyncio.AbstractEventLoop | None:
    if sys.platform != "win32":
        import uvloop
        return uvloop.new_event_loop
    return None


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=get_loop_factory()) as runner:
        runner.run(main())
