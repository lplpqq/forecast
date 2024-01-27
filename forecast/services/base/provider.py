from abc import abstractmethod
from datetime import datetime

from pydantic_extra_types.coordinate import Coordinate

from forecast.models import Granularity
from forecast.services.base import Requestor


class Provider(Requestor):
    @abstractmethod
    async def get_historical_weather(self, granularity: Granularity,
                                     coordinate: Coordinate,
                                     start_date: datetime, end_date: datetime):
        ...
