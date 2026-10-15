import logging
from datetime import UTC, date, datetime

from sqlalchemy import text

from app.actions.calls.create_call_partitions import PARTITIONS_AHEAD
from app.repositories import call_partition_repository
from app.support import partition_maintenance
from tests.factories import create_account, create_call, create_campaign

PARTITIONS_SQL = text("SELECT inhrelid::regclass::text FROM pg_inherits WHERE inhparent = 'calls'::regclass")
STORED_IN_SQL = text("SELECT tableoid::regclass::text FROM calls")


def partition_name(day: date) -> str:
    return f"calls_{day:%Y%m%d}"


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

    assert await session.scalar(STORED_IN_SQL) == "calls_20300301"


async def test_creating_a_partition_moves_that_days_calls_out_of_the_default_partition(session):
    campaign = await create_campaign(session, await create_account(session))
    await create_call(session, campaign, datetime(2030, 4, 1, 12, tzinfo=UTC))
    assert await session.scalar(STORED_IN_SQL) == "calls_default"

    await create_partitions(session, date(2030, 4, 1), date(2030, 4, 2))

    assert await session.scalar(STORED_IN_SQL) == "calls_20300401"
    assert {"calls_20300401", "calls_20300402"} <= await partition_names(session)


async def test_maintenance_creates_partitions_from_today_to_the_days_ahead(session):
    today = datetime.now(UTC).date()

    await partition_maintenance.create_upcoming_partitions()

    assert {partition_name(today), partition_name(today + PARTITIONS_AHEAD)} <= await partition_names(session)


async def test_maintenance_logs_a_failure_instead_of_stopping(monkeypatch, caplog):
    async def fail() -> None:
        raise RuntimeError("Database unreachable")

    monkeypatch.setattr(partition_maintenance, "CreateCallPartitions", lambda session, first_day: fail)

    with caplog.at_level(logging.ERROR):
        await partition_maintenance.create_upcoming_partitions()

    assert "Could not create the upcoming call partitions" in caplog.text
