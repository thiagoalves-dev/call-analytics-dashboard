from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.call_status import CallStatus, call_status_column_type


class Call(Base):
    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer)
    campaign_id: Mapped[int] = mapped_column(Integer)
    external_id: Mapped[str | None] = mapped_column(String(64))
    caller_number: Mapped[str] = mapped_column(String(20))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[CallStatus] = mapped_column(call_status_column_type)
