from abc import ABC
from typing import Generic, TypeVar

from aiohttp import BaseConnector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.client_session_classes import ExtendedClientSession
from forecast.services.base import BaseService

T = TypeVar('T', bound=ExtendedClientSession)


class Service(Generic[T], BaseService, ABC):
    def __init__(
        self,
        base_url: str,
        connector: BaseConnector,
        db_session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._connector = connector

        def client_session_factory(
            connector: BaseConnector,
        ) -> ExtendedClientSession:
            return ExtendedClientSession(base_url, connector)

        self._session_factory = client_session_factory
        self._db_session_factory: async_sessionmaker[AsyncSession] = db_session_factory

        self._aiohttp_session: T | None = None

        super().__init__()

    async def setup(self) -> None:
        await super().setup()

        self._aiohttp_session = self._session_factory(self._connector)

    async def teardown(self) -> None:
        await super().teardown()

        await self._aiohttp_session.close()
