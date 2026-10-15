import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.config import Settings, get_settings
from app.db import SessionLocal, engine
from app.repositories import call_partition_repository
from app.seed.seeder import Seeder

PARTITION_DAYS_AHEAD = 30


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    settings = get_settings()
    await create_partitions(settings)
    await Seeder(engine, settings)()
    await engine.dispose()


async def create_partitions(settings: Settings) -> None:
    today = datetime.now(UTC).date()
    first_day = today - timedelta(days=settings.seed_days + 1)
    async with SessionLocal() as session:
        await call_partition_repository.create_daily_partitions(
            session, first_day, today + timedelta(days=PARTITION_DAYS_AHEAD)
        )
        await session.commit()


asyncio.run(main())
