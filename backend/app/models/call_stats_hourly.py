from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, Table

read_only_views = MetaData()

call_stats_hourly = Table(
    "call_stats_hourly",
    read_only_views,
    Column("bucket", DateTime(timezone=True)),
    Column("account_id", Integer),
    Column("campaign_id", Integer),
    Column("total", BigInteger),
    Column("missed", BigInteger),
    Column("connected", BigInteger),
    Column("converted", BigInteger),
    Column("duration_seconds", BigInteger),
)
