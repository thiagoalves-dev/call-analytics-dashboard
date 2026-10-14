from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Campaign


async def for_account(session: AsyncSession, account_id: int) -> Sequence[Campaign]:
    query = select(Campaign).where(Campaign.account_id == account_id).order_by(Campaign.name)
    return (await session.scalars(query)).all()


async def find_by_tracking_number(session: AsyncSession, account_id: int, tracking_number: str) -> Campaign | None:
    return await session.scalar(
        select(Campaign).where(Campaign.account_id == account_id, Campaign.tracking_number == tracking_number)
    )


async def tracking_numbers_for_account(session: AsyncSession, account_id: int) -> Sequence[str]:
    query = select(Campaign.tracking_number).where(Campaign.account_id == account_id).order_by(Campaign.id)
    return (await session.scalars(query)).all()
