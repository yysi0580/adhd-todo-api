from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.brain_dump import BrainDump
    from app.models.calendar_candidate import CalendarCandidate
    from app.models.calendar_event import CalendarEvent
    from app.models.email_verification_token import EmailVerificationToken
    from app.models.feedback import Feedback
    from app.models.routine import Routine
    from app.models.session import Session
    from app.models.suggestion import Suggestion


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
    brain_dumps: Mapped[list["BrainDump"]] = relationship(back_populates="user")
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="user")
    actions: Mapped[list["Action"]] = relationship(back_populates="user")
    calendar_candidates: Mapped[list["CalendarCandidate"]] = relationship(back_populates="user")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(back_populates="user")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="user")
    routines: Mapped[list["Routine"]] = relationship(back_populates="user")
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        back_populates="user",
    )
