"""Timescale: calls as a hypertable, plus the hourly continuous aggregate.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-13
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SELECT create_hypertable('calls', by_range('started_at', INTERVAL '1 day'))")
    op.execute("CREATE INDEX ix_calls_account_started ON calls (account_id, started_at DESC)")
    op.execute("CREATE INDEX ix_calls_account_ended ON calls (account_id, ended_at DESC)")
    op.execute(
        "CREATE UNIQUE INDEX ux_calls_account_external ON calls (account_id, external_id, started_at) "
        "WHERE external_id IS NOT NULL"
    )
    op.execute(
        """
        CREATE MATERIALIZED VIEW call_stats_hourly
        WITH (timescaledb.continuous, timescaledb.materialized_only = false) AS
        SELECT
            time_bucket(INTERVAL '1 hour', started_at) AS bucket,
            account_id,
            campaign_id,
            count(*) AS total,
            count(*) FILTER (WHERE status = 'missed') AS missed,
            count(*) FILTER (WHERE status = 'connected') AS connected,
            count(*) FILTER (WHERE status = 'converted') AS converted,
            sum(duration_seconds) AS duration_seconds
        FROM calls
        GROUP BY bucket, account_id, campaign_id
        WITH NO DATA
        """
    )
    op.execute("CREATE INDEX ix_call_stats_hourly_account ON call_stats_hourly (account_id, bucket DESC)")
    op.execute(
        """
        SELECT add_continuous_aggregate_policy('call_stats_hourly',
            start_offset => INTERVAL '3 days',
            end_offset => INTERVAL '1 hour',
            schedule_interval => INTERVAL '5 minutes')
        """
    )


def downgrade() -> None:
    op.execute("DROP MATERIALIZED VIEW call_stats_hourly")
    op.execute("DROP INDEX ux_calls_account_external")
    op.execute("DROP INDEX ix_calls_account_ended")
    op.execute("DROP INDEX ix_calls_account_started")
