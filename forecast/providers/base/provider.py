from abc import abstractmethod, ABC
from datetime import datetime

from pydantic_extra_types.coordinate import Coordinate

from forecast.providers.enums import Granularity
from forecast.providers.models import Weather


class Provider(ABC):
    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> dict[Weather]:
        ...

    @property
    @abstractmethod
    def api_key(self) -> str | None:
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        ...
