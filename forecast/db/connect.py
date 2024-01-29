from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from forecast.config import Config


def create_engine(from_config: Config) -> AsyncEngine:
    engine = create_async_engine(
        from_config.db.connection_string,
        echo=False,
    )

    return engine


async def connect(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    return async_session
