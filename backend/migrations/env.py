import asyncio
import re

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import get_settings
from app.models import Base

target_metadata = Base.metadata

CALL_PARTITION_NAME = re.compile(r"^calls_(default|\d{8})$")


def is_call_partition(schema_object, name: str, object_type: str) -> bool:
    if object_type == "table":
        return bool(CALL_PARTITION_NAME.match(name))
    if object_type == "index":
        return bool(CALL_PARTITION_NAME.match(schema_object.table.name))
    return False


def include_object(schema_object, name: str, object_type: str, reflected: bool, compare_to) -> bool:
    return not (reflected and is_call_partition(schema_object, name, object_type))


def run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata, include_object=include_object)
    with context.begin_transaction():
        context.run_migrations()


async def main() -> None:
    database_url = context.get_x_argument(as_dictionary=True).get("url") or get_settings().database_url
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)
    await engine.dispose()


asyncio.run(main())
