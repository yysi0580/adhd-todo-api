from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now
from app.models.session import Session
from app.models.user import User


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=True,
    )
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    suggestion_id: Mapped[int | None] = mapped_column(
        ForeignKey("suggestions.id"),
        index=True,
        nullable=True,
    )
    action_id: Mapped[int | None] = mapped_column(
        ForeignKey("actions.id"),
        index=True,
        nullable=True,
    )
    reaction: Mapped[str] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="feedback")
    session: Mapped[Session] = relationship(back_populates="feedback")
