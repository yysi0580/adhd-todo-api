from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.brain_dump import BrainDump
    from app.models.calendar_candidate import CalendarCandidate
    from app.models.calendar_event import CalendarEvent
    from app.models.feedback import Feedback
    from app.models.suggestion import Suggestion
    from app.models.user import User


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    context_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped["User"] = relationship(back_populates="sessions")
    brain_dumps: Mapped[list["BrainDump"]] = relationship(back_populates="session")
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="session")
    actions: Mapped[list["Action"]] = relationship(back_populates="session")
    calendar_candidates: Mapped[list["CalendarCandidate"]] = relationship(back_populates="session")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(back_populates="session")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="session")
