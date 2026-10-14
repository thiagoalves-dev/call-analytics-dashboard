import asyncio
import logging

from app.config import get_settings
from app.db import engine
from app.seed.seeder import Seeder


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    await Seeder(engine, get_settings())()
    await engine.dispose()


asyncio.run(main())
