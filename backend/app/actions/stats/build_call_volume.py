from collections.abc import Sequence
from datetime import datetime, timedelta

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.call_filter import CallFilter
from app.exceptions import UnprocessableError
from app.models import CallStatus
from app.repositories import call_stats_repository
from app.schemas.stats import Granularity, VolumePoint, VolumeResponse
from app.support.time import local_date, local_midnight, start_of_hour

ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)
MAX_HOURLY_RANGE = timedelta(days=31)


class BuildCallVolume:
    def __init__(
        self, session: AsyncSession, account_id: int, timezone: str, call_filter: CallFilter, granularity: Granularity
    ) -> None:
        self.session = session
        self.account_id = account_id
        self.timezone = timezone
        self.call_filter = call_filter
        self.granularity = granularity

    async def __call__(self) -> VolumeResponse:
        if self.granularity.is_hourly() and self.call_filter.spans_more_than(MAX_HOURLY_RANGE):
            raise UnprocessableError("The hourly view is limited to 31 days; use the daily view")
        rows_by_bucket = {row.bucket: row for row in await self.fetch_rows()}
        points = [self.point(bucket, rows_by_bucket.get(bucket)) for bucket in self.buckets()]
        return VolumeResponse(granularity=self.granularity, timezone=self.timezone, points=points)

    async def fetch_rows(self) -> Sequence[Row]:
        if self.granularity.is_hourly():
            return await call_stats_repository.volume_by_hour(
                self.session, self.account_id, self.call_filter, self.first_bucket()
            )
        return await call_stats_repository.volume_by_local_day(
            self.session, self.account_id, self.call_filter, self.first_bucket(), self.timezone
        )

    def first_bucket(self) -> datetime:
        if self.granularity.is_hourly():
            return start_of_hour(self.call_filter.start)
        return local_midnight(local_date(self.call_filter.start, self.timezone), self.timezone)

    def buckets(self) -> list[datetime]:
        if self.granularity.is_hourly():
            return self.hourly_buckets()
        return self.daily_buckets()

    def hourly_buckets(self) -> list[datetime]:
        buckets = []
        bucket = self.first_bucket()
        while bucket < self.call_filter.end:
            buckets.append(bucket)
            bucket += ONE_HOUR
        return buckets

    def daily_buckets(self) -> list[datetime]:
        buckets = []
        day = local_date(self.call_filter.start, self.timezone)
        while local_midnight(day, self.timezone) < self.call_filter.end:
            buckets.append(local_midnight(day, self.timezone))
            day += ONE_DAY
        return buckets

    @staticmethod
    def point(bucket: datetime, row: Row | None) -> VolumePoint:
        counts = {call_status.value: int(getattr(row, call_status.value)) if row else 0 for call_status in CallStatus}
        return VolumePoint(bucket=bucket, total=sum(counts.values()), **counts)
