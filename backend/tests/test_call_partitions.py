from datetime import UTC, date, datetime

from sqlalchemy import text

from app.repositories import call_partition_repository
from tests.factories import create_account, create_call, create_campaign

PARTITIONS_SQL = text("SELECT inhrelid::regclass::text FROM pg_inherits WHERE inhparent = 'calls'::regclass")


async def partition_names(session) -> set[str]:
    return set((await session.scalars(PARTITIONS_SQL)).all())


async def create_partitions(session, first_day: date, last_day: date) -> None:
    await call_partition_repository.create_daily_partitions(session, first_day, last_day)
    await session.commit()


async def test_creates_one_partition_per_day(session):
    await create_partitions(session, date(2030, 1, 1), date(2030, 1, 3))

    assert {"calls_20300101", "calls_20300102", "calls_20300103"} <= await partition_names(session)


async def test_creating_existing_partitions_again_is_harmless(session):
    await create_partitions(session, date(2030, 2, 1), date(2030, 2, 1))
    await create_partitions(session, date(2030, 2, 1), date(2030, 2, 2))

    assert {"calls_20300201", "calls_20300202"} <= await partition_names(session)


async def test_a_call_is_stored_in_its_days_partition(session):
    await create_partitions(session, date(2030, 3, 1), date(2030, 3, 1))
    campaign = await create_campaign(session, await create_account(session))
    await create_call(session, campaign, datetime(2030, 3, 1, 23, 59, tzinfo=UTC))

    stored_in = await session.scalar(text("SELECT tableoid::regclass::text FROM calls"))

    assert stored_in == "calls_20300301"
