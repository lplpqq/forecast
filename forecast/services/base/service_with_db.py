from typing import Any, TypeAlias

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.services.base.base_service import BaseService

SessionFactory: TypeAlias = async_sessionmaker[AsyncSession]


class ServiceWithDB(BaseService):
    _db_session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, *, db_session_factory: SessionFactory, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self._db_session_factory = db_session_factory
