from abc import abstractmethod
from datetime import datetime
from typing import Any, TypeAlias

import aiohttp
from pydantic import BaseModel
from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.base.requestor import Requestor

HistoricalWeather: TypeAlias = dict[Any, Any] | BaseModel


class Provider(Requestor):
    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> HistoricalWeather:
        ...
