from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import ActionStatus
from app.domain.time import utc_now
from app.models.session import Session
from app.models.user import User

if TYPE_CHECKING:
    from app.models.calendar_event import CalendarEvent


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    suggestion_id: Mapped[int | None] = mapped_column(
        ForeignKey("suggestions.id"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(160))
    micro_step: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=ActionStatus.active.value)
    completion_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    abort_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="actions")
    session: Mapped[Session] = relationship(back_populates="actions")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(back_populates="action")
