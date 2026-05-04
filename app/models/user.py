from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.domain.time import utc_now

if TYPE_CHECKING:
    from app.models.action import Action
    from app.models.brain_dump import BrainDump
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
    feedback: Mapped[list["Feedback"]] = relationship(back_populates="user")
    routines: Mapped[list["Routine"]] = relationship(back_populates="user")
