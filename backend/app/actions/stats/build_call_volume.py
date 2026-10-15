from datetime import datetime

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.stats.bucketing import bucketing_for
from app.exceptions import AuthenticationError
from app.models import CallStatus
from app.repositories import account_repository
from app.schemas.call_filter import CallFilter
from app.schemas.stats import Granularity, VolumePoint, VolumeResponse


class BuildCallVolume:
    def __init__(
        self, session: AsyncSession, account_id: int, call_filter: CallFilter, granularity: Granularity
    ) -> None:
        self.session = session
        self.account_id = account_id
        self.call_filter = call_filter
        self.granularity = granularity

    async def __call__(self) -> VolumeResponse:
        timezone = await self.account_timezone()
        bucketing = bucketing_for(self.granularity, timezone)
        bucketing.ensure_supported(self.call_filter)
        whole_buckets = bucketing.covering(self.call_filter)
        rows = await bucketing.volume(self.session, self.account_id, whole_buckets)
        rows_by_bucket = {row.bucket: row for row in rows}
        points = [self.point(bucket, rows_by_bucket.get(bucket)) for bucket in bucketing.starts_within(whole_buckets)]
        return VolumeResponse(granularity=self.granularity, timezone=timezone, points=points)

    async def account_timezone(self) -> str:
        timezone = await account_repository.timezone_of(self.session, self.account_id)
        if timezone is None:
            raise AuthenticationError("Invalid or expired session")
        return timezone

    @staticmethod
    def point(bucket: datetime, row: Row | None) -> VolumePoint:
        counts = {call_status.value: int(getattr(row, call_status.value)) if row else 0 for call_status in CallStatus}
        return VolumePoint(bucket=bucket, total=sum(counts.values()), **counts)
