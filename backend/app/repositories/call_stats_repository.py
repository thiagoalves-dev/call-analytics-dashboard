from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlalchemy import ColumnElement, Row, func, literal, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.call_filter import CallFilter
from app.models import CallStatus, Campaign, call_stats_hourly

ONE_DAY = timedelta(days=1)

stats = call_stats_hourly.c


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
    local_day = func.time_bucket(ONE_DAY, stats.bucket, timezone)
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
