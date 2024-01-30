from aiohttp import BaseConnector
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.client_session_classes import ExtendedClientSession
from forecast.services.base.service_with_db import ServiceWithDB
from forecast.services.base.service_with_extended_client_session import (
    ServiceWithExtendedClientSession,
)


class MininalServiceWithEverything(
    ServiceWithDB, ServiceWithExtendedClientSession[ExtendedClientSession]
):
    def __init__(
        self,
        base_url: str,
        connector: BaseConnector,
        db_session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        def client_session_factory(
            connector: BaseConnector,
        ) -> ExtendedClientSession:
            return ExtendedClientSession(base_url, connector)

        super().__init__(
            connector=connector,
            db_session_factory=db_session_factory,
            client_session_factory=client_session_factory,
        )
