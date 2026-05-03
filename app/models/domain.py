from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ActionStatus(str, Enum):
    active = "active"
    completed = "completed"
    aborted = "aborted"


class FeedbackType(str, Enum):
    do = "do"
    snooze = "snooze"
    pass_ = "pass"
    make_smaller = "make_smaller"
    capture_only = "capture_only"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    context_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    brain_dumps: Mapped[list["BrainDump"]] = relationship(back_populates="session")
    suggestions: Mapped[list["Suggestion"]] = relationship(back_populates="session")
    actions: Mapped[list["Action"]] = relationship(back_populates="session")
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="session")


class BrainDump(Base):
    __tablename__ = "brain_dumps"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="brain_dumps")


class Suggestion(Base):
    __tablename__ = "suggestions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    brain_dump_id: Mapped[int | None] = mapped_column(ForeignKey("brain_dumps.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    micro_step: Mapped[str] = mapped_column(Text)
    effort_level: Mapped[str] = mapped_column(String(20), default="tiny")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="suggestions")


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    suggestion_id: Mapped[int | None] = mapped_column(ForeignKey("suggestions.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    micro_step: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default=ActionStatus.active.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="actions")


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    suggestion_id: Mapped[int | None] = mapped_column(ForeignKey("suggestions.id"), nullable=True)
    action_id: Mapped[int | None] = mapped_column(ForeignKey("actions.id"), nullable=True)
    reaction: Mapped[str] = mapped_column(String(30))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    session: Mapped[Session] = relationship(back_populates="feedback")
