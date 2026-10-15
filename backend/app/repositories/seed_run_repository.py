from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SeedRun


async def has_completed(session: AsyncSession) -> bool:
    return await session.scalar(select(exists().select_from(SeedRun)))


async def mark_completed(session: AsyncSession) -> None:
    session.add(SeedRun())
    await session.flush()
