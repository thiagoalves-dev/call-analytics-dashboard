import asyncio
import logging
import sys
from datetime import UTC, datetime, timedelta

from app.actions.calls.create_call_partitions import CreateCallPartitions
from app.config import Settings, get_settings
from app.db import SessionLocal, engine
from app.exceptions import IncompleteSeedError
from app.seed.seeder import Seeder

logger = logging.getLogger("app.seed")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    settings = get_settings()
    try:
        await create_partitions(settings)
        await Seeder(engine, settings)()
    finally:
        await engine.dispose()


async def create_partitions(settings: Settings) -> None:
    first_day = datetime.now(UTC).date() - timedelta(days=settings.seed_days + 1)
    async with SessionLocal() as session:
        await CreateCallPartitions(session, first_day)()


try:
    asyncio.run(main())
except IncompleteSeedError as error:
    logger.error("%s", error)
    sys.exit(1)
