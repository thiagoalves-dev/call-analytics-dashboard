from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    source: Mapped[str] = mapped_column(String(100))
    tracking_number: Mapped[str] = mapped_column(String(20), unique=True)
