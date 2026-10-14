"""Core tables: accounts, users, API keys, campaigns, calls.

Revision ID: 0001
Revises:
Create Date: 2026-10-13
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb")

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("password_hash", sa.String(200), nullable=False),
    )
    op.create_index("ix_users_account_id", "users", ["account_id"])
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_api_keys_account_id", "api_keys", ["account_id"])
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("tracking_number", sa.String(20), nullable=False, unique=True),
    )
    op.create_index("ix_campaigns_account_id", "campaigns", ["account_id"])

    op.execute("CREATE TYPE call_status AS ENUM ('missed', 'connected', 'converted')")
    op.create_table(
        "calls",
        sa.Column("id", sa.BigInteger, sa.Identity(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("account_id", sa.Integer, nullable=False),
        sa.Column("campaign_id", sa.Integer, nullable=False),
        sa.Column("external_id", sa.String(64)),
        sa.Column("caller_number", sa.String(20), nullable=False),
        sa.Column("duration_seconds", sa.Integer, nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("missed", "connected", "converted", name="call_status", create_type=False),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", "started_at"),
    )


def downgrade() -> None:
    op.drop_table("calls")
    op.execute("DROP TYPE call_status")
    op.drop_table("campaigns")
    op.drop_table("api_keys")
    op.drop_table("users")
    op.drop_table("accounts")
