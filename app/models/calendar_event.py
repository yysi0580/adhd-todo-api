from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.session import Session
    from app.models.user import User


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int | None] = mapped_column(
        ForeignKey("sessions.id"),
        index=True,
        nullable=True,
    )
    action_id: Mapped[int | None] = mapped_column(
        ForeignKey("actions.id"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Seoul")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(40), default="manual")
    external_uid: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    provider: Mapped[str | None] = mapped_column(String(60), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped["User"] = relationship(back_populates="calendar_events")
    session: Mapped["Session | None"] = relationship(back_populates="calendar_events")
    action: Mapped["Action | None"] = relationship(back_populates="calendar_events")
