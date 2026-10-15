"""Daily partitions for calls, plus the hourly rollup table the charts read.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

CREATE_PARTITIONS_FUNCTION = """
CREATE FUNCTION create_call_partitions(first_day date, last_day date) RETURNS void
LANGUAGE plpgsql AS $$
DECLARE
    day date;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtext('create_call_partitions'));
    FOR day IN SELECT generate_series(first_day, last_day, INTERVAL '1 day')::date LOOP
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF calls FOR VALUES FROM (%L) TO (%L)',
            'calls_' || to_char(day, 'YYYYMMDD'),
            day::timestamp AT TIME ZONE 'UTC',
            (day + 1)::timestamp AT TIME ZONE 'UTC'
        );
    END LOOP;
END;
$$
"""


def upgrade() -> None:
    op.execute(CREATE_PARTITIONS_FUNCTION)
    op.execute("CREATE TABLE calls_default PARTITION OF calls DEFAULT")
    op.execute("CREATE INDEX ix_calls_account_started ON calls (account_id, started_at DESC)")
    op.execute("CREATE INDEX ix_calls_account_ended ON calls (account_id, ended_at DESC)")
    op.execute(
        "CREATE UNIQUE INDEX ux_calls_account_external ON calls (account_id, external_id, started_at) "
        "WHERE external_id IS NOT NULL"
    )
    op.create_table(
        "call_stats_hourly",
        sa.Column("account_id", sa.Integer, nullable=False),
        sa.Column("bucket", sa.DateTime(timezone=True), nullable=False),
        sa.Column("campaign_id", sa.Integer, nullable=False),
        sa.Column("total", sa.BigInteger, nullable=False),
        sa.Column("missed", sa.BigInteger, nullable=False),
        sa.Column("connected", sa.BigInteger, nullable=False),
        sa.Column("converted", sa.BigInteger, nullable=False),
        sa.Column("duration_seconds", sa.BigInteger, nullable=False),
        sa.PrimaryKeyConstraint("account_id", "bucket", "campaign_id"),
    )


def downgrade() -> None:
    op.drop_table("call_stats_hourly")
    op.execute("DROP INDEX ux_calls_account_external")
    op.execute("DROP INDEX ix_calls_account_ended")
    op.execute("DROP INDEX ix_calls_account_started")
    op.execute("DROP TABLE calls_default")
    op.execute("DROP FUNCTION create_call_partitions(date, date)")
