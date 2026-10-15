from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime, timedelta

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import UnprocessableError
from app.repositories import call_stats_repository
from app.schemas.call_filter import CallFilter
from app.schemas.stats import Granularity
from app.support.time import local_date, local_midnight, start_of_hour

ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)
MAX_HOURLY_RANGE = timedelta(days=31)


class Bucketing(ABC):
    @abstractmethod
    def start_of(self, moment: datetime) -> datetime: ...

    @abstractmethod
    def next_after(self, bucket: datetime) -> datetime: ...

    @abstractmethod
    async def volume(self, session: AsyncSession, account_id: int, call_filter: CallFilter) -> Sequence[Row]: ...

    def ensure_supported(self, call_filter: CallFilter) -> None:
        return None

    def covering(self, call_filter: CallFilter) -> CallFilter:
        last_bucket = self.start_of(call_filter.end)
        end = last_bucket if last_bucket == call_filter.end else self.next_after(last_bucket)
        return replace(call_filter, start=self.start_of(call_filter.start), end=end)

    def starts_within(self, call_filter: CallFilter) -> list[datetime]:
        starts = []
        bucket = call_filter.start
        while bucket < call_filter.end:
            starts.append(bucket)
            bucket = self.next_after(bucket)
        return starts


class HourlyBucketing(Bucketing):
    def start_of(self, moment: datetime) -> datetime:
        return start_of_hour(moment)

    def next_after(self, bucket: datetime) -> datetime:
        return bucket + ONE_HOUR

    async def volume(self, session: AsyncSession, account_id: int, call_filter: CallFilter) -> Sequence[Row]:
        return await call_stats_repository.volume_by_hour(session, account_id, call_filter)

    def ensure_supported(self, call_filter: CallFilter) -> None:
        if call_filter.spans_more_than(MAX_HOURLY_RANGE):
            raise UnprocessableError(f"The hourly view is limited to {MAX_HOURLY_RANGE.days} days; use the daily view")


class LocalDailyBucketing(Bucketing):
    def __init__(self, timezone: str) -> None:
        self.timezone = timezone

    def start_of(self, moment: datetime) -> datetime:
        return local_midnight(local_date(moment, self.timezone), self.timezone)

    def next_after(self, bucket: datetime) -> datetime:
        return local_midnight(local_date(bucket, self.timezone) + ONE_DAY, self.timezone)

    async def volume(self, session: AsyncSession, account_id: int, call_filter: CallFilter) -> Sequence[Row]:
        return await call_stats_repository.volume_by_local_day(session, account_id, call_filter, self.timezone)


def bucketing_for(granularity: Granularity, timezone: str) -> Bucketing:
    return HourlyBucketing() if granularity.is_hourly() else LocalDailyBucketing(timezone)
