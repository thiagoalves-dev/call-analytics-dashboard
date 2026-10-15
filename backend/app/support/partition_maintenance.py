import asyncio
import logging
from datetime import UTC, datetime

from app.actions.calls.create_call_partitions import CreateCallPartitions
from app.db import SessionLocal

logger = logging.getLogger(__name__)

MAINTENANCE_INTERVAL_SECONDS = 60 * 60


async def maintain_call_partitions() -> None:
    while True:
        await create_upcoming_partitions()
        await asyncio.sleep(MAINTENANCE_INTERVAL_SECONDS)


async def create_upcoming_partitions() -> None:
    try:
        async with SessionLocal() as session:
            await CreateCallPartitions(session, datetime.now(UTC).date())()
    except Exception:
        logger.exception("Could not create the upcoming call partitions")
