from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(url: str) -> AsyncEngine:
    engine = create_async_engine(url, echo=False, pool_size=50)

    return engine


async def connect(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    async_session = async_sessionmaker(engine, expire_on_commit=True, autoflush=True)

    return async_session
