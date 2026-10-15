from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import ColumnElement, Row, func, literal, select, true
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.call_filter import CallFilter
from app.models import Call, CallStatus, Campaign, call_stats_hourly
from app.support.time import start_of_hour

COUNTERS = ("total", *(call_status.value for call_status in CallStatus), "duration_seconds")

stats = call_stats_hourly.c


async def record_call(session: AsyncSession, call: Call) -> None:
    statement = insert(call_stats_hourly).values(
        account_id=call.account_id,
        bucket=start_of_hour(call.started_at),
        campaign_id=call.campaign_id,
        total=1,
        **{call_status.value: int(call.status == call_status) for call_status in CallStatus},
        duration_seconds=call.duration_seconds,
    )
    await session.execute(
        statement.on_conflict_do_update(
            index_elements=[stats.account_id, stats.bucket, stats.campaign_id],
            set_={counter: stats[counter] + statement.excluded[counter] for counter in COUNTERS},
        )
    )


async def volume_by_hour(
    session: AsyncSession, account_id: int, call_filter: CallFilter, start: datetime
) -> Sequence[Row]:
    query = (
        select(stats.bucket.label("bucket"), *status_totals(call_filter))
        .where(*filter_conditions(account_id, call_filter, start))
        .group_by(stats.bucket)
    )
    return (await session.execute(query)).all()


async def volume_by_local_day(
    session: AsyncSession, account_id: int, call_filter: CallFilter, start: datetime, timezone: str
) -> Sequence[Row]:
    local_day = func.date_trunc("day", stats.bucket, timezone)
    query = (
        select(local_day.label("bucket"), *status_totals(call_filter))
        .where(*filter_conditions(account_id, call_filter, start))
        .group_by(local_day)
    )
    return (await session.execute(query)).all()


async def conversion_by(
    session: AsyncSession, account_id: int, call_filter: CallFilter, start: datetime, group_column: ColumnElement
) -> Sequence[Row]:
    query = (
        select(
            group_column.label("key"),
            func.min(Campaign.name).label("campaign_name"),
            func.min(Campaign.source).label("source"),
            func.sum(stats.total).label("calls"),
            *[func.sum(stats[call_status.value]).label(call_status.value) for call_status in CallStatus],
        )
        .join(Campaign, Campaign.id == stats.campaign_id)
        .where(*filter_conditions(account_id, call_filter, start))
        .group_by(group_column)
    )
    return (await session.execute(query)).all()


def status_totals(call_filter: CallFilter) -> list[ColumnElement]:
    included = call_filter.included_statuses()
    return [
        (func.sum(stats[call_status.value]) if call_status in included else literal(0)).label(call_status.value)
        for call_status in CallStatus
    ]


def filter_conditions(account_id: int, call_filter: CallFilter, start: datetime) -> list[ColumnElement]:
    return [
        stats.account_id == account_id,
        stats.bucket >= start,
        stats.bucket < call_filter.end,
        stats.campaign_id.in_(call_filter.campaign_ids) if call_filter.campaign_ids else true(),
    ]
