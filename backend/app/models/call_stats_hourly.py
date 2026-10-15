from sqlalchemy import BigInteger, Column, DateTime, Integer, Table

from app.models.base import Base

call_stats_hourly = Table(
    "call_stats_hourly",
    Base.metadata,
    Column("account_id", Integer, primary_key=True),
    Column("bucket", DateTime(timezone=True), primary_key=True),
    Column("campaign_id", Integer, primary_key=True),
    Column("total", BigInteger, nullable=False),
    Column("missed", BigInteger, nullable=False),
    Column("connected", BigInteger, nullable=False),
    Column("converted", BigInteger, nullable=False),
    Column("duration_seconds", BigInteger, nullable=False),
)
