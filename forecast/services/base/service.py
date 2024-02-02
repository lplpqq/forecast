from abc import ABC
from typing import Any, Generic, TypeVar

from aiohttp import BaseConnector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.client_session_classes import ExtendedClientSession
from forecast.services.base import BaseService

T = TypeVar('T', bound=ExtendedClientSession)


class Service(Generic[T], BaseService, ABC):
    def __init__(
        self,
        db_session_factory: async_sessionmaker[AsyncSession],
        *,
        connector: BaseConnector | None = None,
        **client_session_kwargs: Any,
    ) -> None:
        self._db_session_factory: async_sessionmaker[AsyncSession] = db_session_factory

        self._connector = connector
        self._aiohttp_session: T | None = None

        self._client_session_kwargs = client_session_kwargs

        super().__init__()

    async def _setup_aiohttp_session(self) -> None:
        self._aiohttp_session = ExtendedClientSession(
            connector=self._connector, **self._client_session_kwargs
        )

    async def setup(self) -> None:
        await super().setup()

        if self._connector is not None:
            await self._setup_aiohttp_session()

    async def teardown(self) -> None:
        await super().teardown()

        await self._aiohttp_session.close()
