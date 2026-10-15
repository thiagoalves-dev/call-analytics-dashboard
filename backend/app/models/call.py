from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Identity, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.call_status import CallStatus, call_status_column_type


class Call(Base):
    __tablename__ = "calls"
    __table_args__ = (
        Index("ix_calls_account_started", "account_id", text("started_at DESC")),
        Index("ix_calls_account_ended", "account_id", text("ended_at DESC")),
        Index(
            "ux_calls_account_external",
            "account_id",
            "external_id",
            "started_at",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
        {"postgresql_partition_by": "RANGE (started_at)"},
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer)
    campaign_id: Mapped[int] = mapped_column(Integer)
    external_id: Mapped[str | None] = mapped_column(String(64))
    caller_number: Mapped[str] = mapped_column(String(20))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[CallStatus] = mapped_column(call_status_column_type)
