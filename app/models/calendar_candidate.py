from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import (
    CalendarCandidateStatus,
    CalendarCandidateType,
    CalendarEnergyLevel,
    CalendarFrictionLevel,
    CalendarPreferredTimeBlock,
    CalendarSplitStrategy,
)
from app.domain.time import utc_now

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.session import Session
    from app.models.suggestion import Suggestion
    from app.models.user import User


class CalendarCandidate(Base):
    __tablename__ = "calendar_candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"), index=True)
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
    title: Mapped[str] = mapped_column(String(160))
    micro_step: Mapped[str] = mapped_column(Text)
    candidate_type: Mapped[str] = mapped_column(
        String(30),
        default=CalendarCandidateType.flexible.value,
    )
    estimated_minutes: Mapped[int] = mapped_column(Integer)
    min_minutes: Mapped[int] = mapped_column(Integer)
    max_minutes: Mapped[int] = mapped_column(Integer)
    preferred_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    earliest_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    latest_end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    preferred_time_block: Mapped[str] = mapped_column(
        String(30),
        default=CalendarPreferredTimeBlock.anytime.value,
    )
    energy_level: Mapped[str] = mapped_column(String(20), default=CalendarEnergyLevel.medium.value)
    friction_level: Mapped[str] = mapped_column(
        String(20),
        default=CalendarFrictionLevel.medium.value,
    )
    split_strategy: Mapped[str] = mapped_column(
        String(30),
        default=CalendarSplitStrategy.single_block.value,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=CalendarCandidateStatus.proposed.value,
        index=True,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(80), default="Asia/Seoul")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped["User"] = relationship(back_populates="calendar_candidates")
    session: Mapped["Session"] = relationship(back_populates="calendar_candidates")
    suggestion: Mapped["Suggestion | None"] = relationship(back_populates="calendar_candidates")
    action: Mapped["Action | None"] = relationship()
