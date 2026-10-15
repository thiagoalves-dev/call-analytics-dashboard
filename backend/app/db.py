from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

POOL_SIZE = 10
MAX_OVERFLOW = 10

engine = create_async_engine(get_settings().database_url, pool_size=POOL_SIZE, max_overflow=MAX_OVERFLOW)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
