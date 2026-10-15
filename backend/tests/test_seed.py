import pytest
from sqlalchemy import func, select

from app.config import Settings
from app.db import engine
from app.exceptions import IncompleteSeedError
from app.models import Account
from app.seed.demo_accounts import DEMO_ACCOUNTS
from app.seed.seeder import Seeder
from tests.factories import create_account

SMALL_SEED = Settings(seed_calls_per_account=50, seed_days=2)


async def count_accounts(session) -> int:
    return await session.scalar(select(func.count()).select_from(Account))


async def test_refuses_to_continue_a_seed_that_never_finished(session):
    await create_account(session)

    with pytest.raises(IncompleteSeedError, match="docker compose down -v"):
        await Seeder(engine, SMALL_SEED)()

    assert await count_accounts(session) == 1


async def test_a_finished_seed_is_not_repeated(session):
    await Seeder(engine, SMALL_SEED)()
    await Seeder(engine, SMALL_SEED)()

    assert await count_accounts(session) == len(DEMO_ACCOUNTS)
