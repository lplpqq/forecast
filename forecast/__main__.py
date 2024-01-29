import asyncio
from datetime import datetime

import uvloop
from aiohttp import TCPConnector
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.providers.enums import Granularity
from forecast.logging import logger_provider
from forecast.providers import WeatherBit, OpenMeteo, WorldWeatherOnline

logger = logger_provider(__name__)


async def main() -> None:
    logger.info('Starting')

    # engine = create_engine(config)
    # session_factory = await connect(engine)
    #
    # async with session_factory() as session:
    #     get_hourly_weather_query = select(models.HourlyWeather).limit(10)
    #     hourly_weather = (await session.scalars(get_hourly_weather_query)).all()
    #
    #     print(hourly_weather)

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

        # async with Meteostat(connector) as meteostat:
        #     print(
        #         await meteostat.get_historical_weather(
        #             Granularity.HOUR,
        #             Coordinate(
        #                 latitude=Latitude(35.6897), longitude=Longitude(139.6922)
        #             ),
        #             start_date=datetime(2010, 1, 5),
        #             end_date=datetime(2024, 1, 15),
        #         )
        #     )

        weatherbit = WeatherBit(connector, '3bc5d56a89f247758f55c4023ad95035')
        await weatherbit.setup()
        weatherbit_data = await weatherbit.get_historical_weather(
            Granularity.HOUR,
            location,
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        )

        openmeteo = OpenMeteo(connector)
        await openmeteo.setup()
        openmeteo_data = await openmeteo.get_historical_weather(
            Granularity.HOUR,
            location,
            start_date=datetime(2024, 1, 5),
            end_date=datetime(2024, 1, 15)
        )

        for world_weather_, weathebit_, openmeteo_ in zip(
                world_weather_data, weatherbit_data, openmeteo_data
        ):
            print(world_weather_)
            print(weathebit_)
            print(openmeteo_)
            print()

        # async with Tomorrow(connector, config.data_sources.tomorrow.api_key) as tomorrow:
        #     print(await tomorrow.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(
        #             latitude=Latitude(
        #                 35.6897
        #             ),
        #             longitude=Longitude(
        #                 139.6922
        #             )
        #         ),
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15)
        #     ))

        # openweathermap = OpenWeatherMap(connector, config.data_sources.open_weather_map.api_key)
        # await openweathermap.setup()
        # print(await openweathermap.get_historical_weather(
        #     Granularity.HOUR,
        #     Coordinate(
        #         latitude=Latitude(
        #            35.6897
        #         ),
        #         longitude=Longitude(
        #             139.6922
        #         )
        #     ),
        #     start_date=datetime(2024, 1, 5),
        #     end_date=datetime(2024, 1, 15)
        # ))

        # visualcrossing = VisualCrossing(connector, config.data_sources.visual_crossing.api_key)
        # await visualcrossing.setup()
        # print(
        #     await visualcrossing.get_historical_weather(
        #         Granularity.HOUR,
        #         Coordinate(
        #             latitude=Latitude(
        #                 35.6897
        #             ),
        #             longitude=Longitude(
        #                 139.6922
        #             )
        #         ),
        #         start_date=datetime(2024, 1, 5),
        #         end_date=datetime(2024, 1, 15),
        #     )
        # )


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        runner.run(main())

# app = FastAPI()
#
#
# @app.get("/")
# async def root():
#     return {"message": "Hello World"}
#
#
# @app.get("/hello/{name}")
# async def say_hello(name: str):
#     return {"message": f"Hello {name}"}
