from abc import abstractmethod
from datetime import datetime
from typing import Any, TypeAlias

import aiohttp
from pydantic import BaseModel
from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.providers.base.requestor import Requestor

HistoricalWeather: TypeAlias = dict[Any, Any] | BaseModel


class Provider(Requestor):
    @abstractmethod
    def __init__(self, conn: aiohttp.TCPConnector, api_key: str | None = None) -> None:
        ...

    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> HistoricalWeather:
        ...
