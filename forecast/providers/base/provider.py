from abc import ABC, abstractmethod
from datetime import datetime

import aiohttp
from pydantic_extra_types.coordinate import Coordinate

from forecast.api_client_session import ApiClientSession
from forecast.logging import logger_provider
from forecast.providers.enums import Granularity
from forecast.providers.models import Weather
from forecast.utils import pascal_case_to_snake_case


class Provider(ABC):
    def __init__(
        self,
        base_url: str,
        connector: aiohttp.BaseConnector,
        api_key: str | None = None,
    ) -> None:
        self.logger = logger_provider(__name__)

        self._base_url = base_url
        self._connector = connector
        self._api_key = api_key

        self._session: ApiClientSession | None = None

        self.is_setup = False
        self.was_turndown_up = False

        self.name = pascal_case_to_snake_case(self.__class__.__name__)

    async def setup(self) -> None:
        if self.was_turndown_up:
            self.logger.warning(
                'This provider has already been turndown. You may not setup it again'
            )
            return

        if self.is_setup:
            self.logger.warning(
                "The provider is already setup, you shouldn't setup it twice"
            )
            return

        self._session = ApiClientSession(self._base_url, self._api_key, self._connector)
        self.is_setup = True

    async def turndown(self) -> None:
        # * The None check is done in order to silence the type checker, it's not able to infer that the self.is_setup is a TypeGuard for the self._session
        if not self.is_setup or self._session is None:
            self.logger.warning(
                'No need to class durndown the class before it was setup.'
            )
            return

        await self._session.close()
        self.was_turndown_up = True

    @property
    def session(self) -> ApiClientSession:
        if not self.is_setup or self._session is None:
            raise ValueError(
                'The provider was never setup. Either manually call the setup method or use an async context manager'
            )

        return self._session

    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Granularity,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Weather]:
        ...

    @property
    def api_key(self) -> str | None:
        return self._api_key
