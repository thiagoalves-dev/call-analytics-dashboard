from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select

from app.config import Settings
from app.db import engine
from app.exceptions import IncompleteSeedError
from app.models import Account, Call
from app.repositories import seed_run_repository
from app.seed.demo_accounts import DEMO_ACCOUNTS, SUMMIT
from app.seed.seeder import Seeder
from tests.factories import create_account

SMALL_SEED = Settings(seed_calls_per_account=50, seed_days=2)
EXACT_SEED = Settings(seed_calls_per_account=100_000, seed_days=3)
MIDDAY = datetime(2026, 10, 1, 17, tzinfo=UTC)
HALF_AN_HOUR_AFTER_NEW_YORK_MIDNIGHT = datetime(2026, 10, 1, 4, 30, tzinfo=UTC)
HOURS_PER_DAY = 24
ROUNDING_TOLERANCE = HOURS_PER_DAY * EXACT_SEED.seed_days * len(SUMMIT.campaigns) / 2


async def count_accounts(session) -> int:
    return await session.scalar(select(func.count()).select_from(Account))


async def calls_per_account(session) -> dict[str, int]:
    query = (
        select(Account.name, func.count(Call.id)).outerjoin(Call, Call.account_id == Account.id).group_by(Account.name)
    )
    return dict((await session.execute(query)).all())


async def test_refuses_to_continue_a_seed_that_never_finished(session):
    await create_account(session)

    with pytest.raises(IncompleteSeedError, match="docker compose down -v"):
        await Seeder(engine, SMALL_SEED)()

    assert await count_accounts(session) == 1


async def test_a_finished_seed_is_not_repeated(session):
    await Seeder(engine, SMALL_SEED)()
    await Seeder(engine, SMALL_SEED)()

    assert await count_accounts(session) == len(DEMO_ACCOUNTS)


async def test_seeds_the_configured_number_of_calls_per_account(session):
    await Seeder(engine, EXACT_SEED, now=MIDDAY)()

    for seeded in (await calls_per_account(session)).values():
        assert abs(seeded - EXACT_SEED.seed_calls_per_account) <= ROUNDING_TOLERANCE


async def test_seeds_nothing_for_a_day_whose_first_hour_has_not_finished(session):
    await Seeder(engine, Settings(seed_calls_per_account=50, seed_days=1), now=HALF_AN_HOUR_AFTER_NEW_YORK_MIDNIGHT)()

    assert (await calls_per_account(session))[SUMMIT.name] == 0
    assert await seed_run_repository.has_completed(session)
