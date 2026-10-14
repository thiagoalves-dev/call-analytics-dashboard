import asyncio
import statistics
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import text

from app.db import engine

RUNS = 5
ACCOUNT_ID = 1
TIMEZONE = "America/Chicago"

RAW_COUNTS = """
    count(*) AS total,
    count(*) FILTER (WHERE status = 'missed') AS missed,
    count(*) FILTER (WHERE status = 'connected') AS connected,
    count(*) FILTER (WHERE status = 'converted') AS converted
"""
AGGREGATE_COUNTS = "sum(total), sum(missed), sum(connected), sum(converted)"


@dataclass(frozen=True)
class Scenario:
    name: str
    days: int
    raw_sql: str
    aggregate_sql: str


SCENARIOS = (
    Scenario(
        "Hourly volume, last 7 days",
        7,
        f"SELECT time_bucket('1 hour', started_at) AS bucket, {RAW_COUNTS} FROM calls "
        "WHERE account_id = :account AND started_at >= :start AND started_at < :end GROUP BY bucket",
        f"SELECT bucket, {AGGREGATE_COUNTS} FROM call_stats_hourly "
        "WHERE account_id = :account AND bucket >= :start AND bucket < :end GROUP BY bucket",
    ),
    Scenario(
        "Daily volume, last 90 days",
        90,
        f"SELECT time_bucket('1 day', started_at, :timezone) AS bucket, {RAW_COUNTS} FROM calls "
        "WHERE account_id = :account AND started_at >= :start AND started_at < :end GROUP BY bucket",
        f"SELECT time_bucket('1 day', bucket, :timezone) AS day, {AGGREGATE_COUNTS} FROM call_stats_hourly "
        "WHERE account_id = :account AND bucket >= :start AND bucket < :end GROUP BY day",
    ),
    Scenario(
        "Conversion by campaign, last 30 days",
        30,
        f"SELECT campaign_id, {RAW_COUNTS} FROM calls "
        "WHERE account_id = :account AND started_at >= :start AND started_at < :end GROUP BY campaign_id",
        f"SELECT campaign_id, {AGGREGATE_COUNTS} FROM call_stats_hourly "
        "WHERE account_id = :account AND bucket >= :start AND bucket < :end GROUP BY campaign_id",
    ),
)


async def median_milliseconds(sql: str, parameters: dict) -> float:
    timings = []
    async with engine.connect() as connection:
        for _ in range(RUNS):
            started = time.perf_counter()
            await connection.execute(text(sql), parameters)
            timings.append((time.perf_counter() - started) * 1000)
    return statistics.median(timings)


def parameters_for(scenario: Scenario) -> dict:
    end = datetime.now(UTC)
    return {"account": ACCOUNT_ID, "timezone": TIMEZONE, "start": end - timedelta(days=scenario.days), "end": end}


async def table_facts() -> tuple[int, str]:
    async with engine.connect() as connection:
        row_count = await connection.scalar(text("SELECT count(*) FROM calls"))
        size = await connection.scalar(text("SELECT pg_size_pretty(hypertable_size('calls'))"))
    return row_count, size


async def main() -> None:
    row_count, size = await table_facts()
    print(f"calls: {row_count:,} rows, {size} on disk. Median of {RUNS} runs, account {ACCOUNT_ID}.\n")
    print("| Query | Raw calls table | Continuous aggregate | Speedup |")
    print("|---|---:|---:|---:|")
    for scenario in SCENARIOS:
        raw = await median_milliseconds(scenario.raw_sql, parameters_for(scenario))
        aggregate = await median_milliseconds(scenario.aggregate_sql, parameters_for(scenario))
        print(f"| {scenario.name} | {raw:,.0f} ms | {aggregate:,.1f} ms | {raw / aggregate:,.0f}x |")
    await engine.dispose()


asyncio.run(main())
