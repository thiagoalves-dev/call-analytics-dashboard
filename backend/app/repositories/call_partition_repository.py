from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_daily_partitions(session: AsyncSession, first_day: date, last_day: date) -> None:
    await session.execute(
        text("SELECT create_call_partitions(:first_day, :last_day)"), {"first_day": first_day, "last_day": last_day}
    )
