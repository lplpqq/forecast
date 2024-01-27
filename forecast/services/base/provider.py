from abc import abstractmethod
from datetime import datetime
from typing import Any

from pydantic_extra_types.coordinate import Coordinate

from forecast.enums import Granularity
from forecast.services.base.requestor import Requestor


class Provider(Requestor):
    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[Any, Any]:
        ...
