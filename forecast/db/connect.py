from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from forecast.config import Config


def create_engine(url: str) -> AsyncEngine:
    engine = create_async_engine(url, echo=False, pool_size=500)

    return engine


async def connect(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    return async_session
