from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.enums import SuggestionGenerationType, SuggestionSource
from app.domain.time import utc_now
from app.models.session import Session
from app.models.user import User


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    brain_dump_id: Mapped[int | None] = mapped_column(
        ForeignKey("brain_dumps.id"),
        nullable=True,
    )
    parent_suggestion_id: Mapped[int | None] = mapped_column(
        ForeignKey("suggestions.id"),
        index=True,
        nullable=True,
    )
    generation_type: Mapped[str] = mapped_column(
        String(30),
        default=SuggestionGenerationType.original.value,
    )
    source: Mapped[str] = mapped_column(String(30), default=SuggestionSource.rule_based.value)
    title: Mapped[str] = mapped_column(String(160))
    micro_step: Mapped[str] = mapped_column(Text)
    effort_level: Mapped[str] = mapped_column(String(20), default="tiny")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="suggestions")
    session: Mapped[Session] = relationship(back_populates="suggestions")
