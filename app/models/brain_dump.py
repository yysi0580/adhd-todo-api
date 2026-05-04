from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now
from app.models.session import Session
from app.models.user import User


class BrainDump(Base):
    __tablename__ = "brain_dumps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="brain_dumps")
    session: Mapped[Session] = relationship(back_populates="brain_dumps")
