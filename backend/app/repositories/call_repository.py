from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Row, select, true
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.call_filter import CallFilter
from app.models import Call, Campaign


async def insert_unless_duplicate(session: AsyncSession, values: dict) -> Call | None:
    statement = (
        insert(Call)
        .values(**values)
        .on_conflict_do_nothing(
            index_elements=["account_id", "external_id", "started_at"], index_where=Call.external_id.isnot(None)
        )
        .returning(Call)
    )
    return await session.scalar(statement)


async def find_by_external_id(
    session: AsyncSession, account_id: int, external_id: str, started_at: datetime
) -> Call | None:
    return await session.scalar(
        select(Call).where(
            Call.account_id == account_id, Call.external_id == external_id, Call.started_at == started_at
        )
    )


async def most_recent(
    session: AsyncSession, account_id: int, call_filter: CallFilter, limit: int
) -> Sequence[Row[tuple[Call, Campaign]]]:
    query = (
        select(Call, Campaign)
        .join(Campaign, Campaign.id == Call.campaign_id)
        .where(
            Call.account_id == account_id,
            Call.started_at >= call_filter.start,
            Call.started_at < call_filter.end,
            Call.campaign_id.in_(call_filter.campaign_ids) if call_filter.campaign_ids else true(),
            Call.status.in_(call_filter.statuses) if call_filter.statuses else true(),
        )
        .order_by(Call.ended_at.desc(), Call.id.desc())
        .limit(limit)
    )
    return (await session.execute(query)).all()
