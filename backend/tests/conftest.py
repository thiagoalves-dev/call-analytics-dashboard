import subprocess

import pytest
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.config import get_settings
from app.db import engine
from app.main import app
from app.services.broadcaster import Broadcaster

TABLES = "accounts, users, api_keys, campaigns, calls"


@pytest.fixture(scope="session", autouse=True)
async def database():
    database_url = make_url(get_settings().database_url)
    await recreate_database(database_url)
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    yield
    await engine.dispose()


async def recreate_database(database_url) -> None:
    admin_engine = create_async_engine(database_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as connection:
        await connection.execute(text(f"DROP DATABASE IF EXISTS {database_url.database} WITH (FORCE)"))
        await connection.execute(text(f"CREATE DATABASE {database_url.database}"))
    await admin_engine.dispose()


@pytest.fixture(autouse=True)
async def clean_tables():
    async with engine.begin() as connection:
        await connection.execute(text(f"TRUNCATE {TABLES} RESTART IDENTITY CASCADE"))


@pytest.fixture
async def session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(scope="session")
async def broadcaster():
    redis = Redis.from_url(get_settings().redis_url)
    broadcaster = Broadcaster(redis)
    await broadcaster.start()
    app.state.broadcaster = broadcaster
    yield broadcaster
    await broadcaster.stop()
    await redis.aclose()


@pytest.fixture
async def client(broadcaster):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
