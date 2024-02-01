import asyncio
from asyncio import AbstractEventLoop
from abc import ABC, abstractmethod
from datetime import datetime
from types import TracebackType

from aiohttp import BaseConnector
from pydantic_extra_types.coordinate import Coordinate

from forecast.client_session_classes.extended_client_session import ExtendedClientSession
from forecast.logging import logger_provider
from forecast.providers.models import Weather
from forecast.utils import pascal_case_to_snake_case


class Provider(ABC):
    def __init__(
        self,
        base_url: str,
        connector: BaseConnector,
        api_key: str | None = None,
        *,
        event_loop: AbstractEventLoop = None
    ) -> None:
        self.logger = logger_provider(__name__)

        self._base_url = base_url
        self._connector = connector
        self._api_key = api_key
        self._event_loop = event_loop

        self._session: ExtendedClientSession | None = None

        self.is_setup = False
        self.was_torn_down = False

        self.name = pascal_case_to_snake_case(self.__class__.__name__)

    async def setup(self) -> None:
        if self.was_torn_down:
            self.logger.warning(
                'This provider has already been teared down. You may not set it up again'
            )
            return

        if self.is_setup:
            self.logger.warning(
                "The provider is already setup, you shouldn't setup it twice"
            )
            return

        self._session = ExtendedClientSession(self._base_url, self._connector)
        self.is_setup = True

    async def teardown(self) -> None:
        # * The None check is done in order to silence the type checker, it's not able to infer that the self.is_setup is a TypeGuard for the self._session
        if not self.is_setup or self._session is None:
            self.logger.warning('No need to tear down the class before it was setup.')
            return

        await self._session.close()
        self.was_torn_down = True

    async def __aenter__(self) -> None:
        await self.setup()

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        await self.teardown()

    @property
    def session(self) -> ExtendedClientSession:
        if not self.is_setup or self._session is None:
            raise ValueError(
                'The provider was never setup. Either manually call the setup method or use an async context manager'
            )

        return self._session

    @abstractmethod
    async def get_historical_weather(
        self,
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> list[Weather]:
        ...
