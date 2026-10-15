from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SeedRun(Base):
    __tablename__ = "seed_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
