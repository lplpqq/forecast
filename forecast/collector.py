"""
scrap all info and put into database
"""
from datetime import datetime
from typing import Any

from pydantic_extra_types.coordinate import Coordinate
from providers.base import Provider

from forecast.enums import Granularity

# FIXME: I don't really know where I should put this file.


class Collector:
    def __init__(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ):
        self._granularity = granularity
        self._coordinate = coordinate
        self._start_date = start_date
        self._end_date = end_date

    async def _save_collected_data(self, *args: Any) -> None:
        # todo add to database
        ...

    async def _collect_provider(self, provider: Provider) -> None:
        await provider.get_historical_weather(
            self._granularity, self._coordinate, self._start_date, self._end_date
        )

    async def collect_all_providers(self) -> None:
        # FIXME: Going throgh all of the bloody globals and checking their types has to be close. I think we should use importlib if we want to import everything dinamically. OTHERWISE, provide the classes manually, there are really that many of those.
        providers = [
            cls
            for cls in globals().values()
            if isinstance(cls, type) and issubclass(cls, Provider)
        ]
        for provider in providers:
            await self._collect_provider(provider)
