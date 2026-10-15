from datetime import UTC, date, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import call_partition_repository

PARTITIONS_AHEAD = timedelta(days=30)


class CreateCallPartitions:
    def __init__(self, session: AsyncSession, first_day: date) -> None:
        self.session = session
        self.first_day = first_day

    async def __call__(self) -> None:
        last_day = datetime.now(UTC).date() + PARTITIONS_AHEAD
        await call_partition_repository.create_daily_partitions(self.session, self.first_day, last_day)
        await self.session.commit()
