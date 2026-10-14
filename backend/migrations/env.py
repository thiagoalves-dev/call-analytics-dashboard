import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.models import Base

target_metadata = Base.metadata


def run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def main() -> None:
    database_url = context.get_x_argument(as_dictionary=True).get("url") or get_settings().database_url
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


asyncio.run(main())
