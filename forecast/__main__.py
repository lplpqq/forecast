import asyncio

import uvloop

from forecast.logging import logger_provider

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

    # async with TCPConnector() as connector:
    # weatherbit = WeatherBit(connector, '3bc5d56a89f247758f55c4023ad95035')
    # await weatherbit.setup()
    # print(await weatherbit.get_historical_weather(
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
    # ))

    # async with OpenMeteo(connector) as openmeteo:
    # print(await openmeteo.get_historical_weather(
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
    # ))
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
