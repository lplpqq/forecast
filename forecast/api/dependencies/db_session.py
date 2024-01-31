from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from forecast.config import config
from forecast.db.connect import connect, create_engine


class SessionFactoryProvider:
    def __init__(self) -> None:
        self._engine = create_engine(config)
        self._session_factory: None | async_sessionmaker[AsyncSession] = None

    async def __call__(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is not None:
            return self._session_factory

        self._session_factory = await connect(self._engine)
        return self._session_factory


session_factory_provider = SessionFactoryProvider()


async def db_session() -> AsyncIterator[AsyncSession]:
    session_factory = await session_factory_provider()

    async with session_factory() as session:
        yield session


InjectedDBSesssion = Annotated[AsyncSession, Depends(db_session)]
