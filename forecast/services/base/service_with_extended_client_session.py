from collections.abc import Callable
from typing import Any, Generic, TypeVar

from aiohttp import BaseConnector

from forecast.client_session_classes.extended_client_session import (
    ExtendedClientSession,
)
from forecast.services.base.base_service import BaseService

T = TypeVar('T', bound=ExtendedClientSession)


class ServiceWithExtendedClientSession(Generic[T], BaseService):
    _aiohttp_session: T

    def __init__(
        self,
        *,
        connector: BaseConnector,
        client_session_factory: Callable[[BaseConnector], T],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)

        self._connector = connector
        self._session_factory = client_session_factory

    async def setup(self) -> None:
        self._aiohttp_session = self._session_factory(self._connector)

        return await super().setup()

    async def teardown(self) -> None:
        await self._aiohttp_session.close()

        return await super().teardown()
