from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    context_note: str | None = None


class SessionRead(BaseModel):
    id: int
    context_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class BrainDumpCreate(BaseModel):
    session_id: int | None = None
    raw_text: str = Field(min_length=1, max_length=5000)


class BrainDumpRead(BaseModel):
    id: int
    session_id: int
    raw_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SuggestionRead(BaseModel):
    id: int
    session_id: int
    brain_dump_id: int | None
    title: str
    micro_step: str
    effort_level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BrainDumpResponse(BaseModel):
    session: SessionRead
    brain_dump: BrainDumpRead
    suggestions: list[SuggestionRead]


class ActionStatus(StrEnum):
    active = "active"
    completed = "completed"
    aborted = "aborted"


class ActionCreate(BaseModel):
    session_id: int
    suggestion_id: int | None = None
    title: str | None = None
    micro_step: str | None = None


class ActionUpdate(BaseModel):
    status: ActionStatus


class ActionRead(BaseModel):
    id: int
    session_id: int
    suggestion_id: int | None
    title: str
    micro_step: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


FeedbackReaction = Literal["do", "snooze", "pass", "make_smaller", "capture_only"]


class FeedbackCreate(BaseModel):
    session_id: int
    suggestion_id: int | None = None
    action_id: int | None = None
    reaction: FeedbackReaction
    note: str | None = None


class FeedbackRead(BaseModel):
    id: int
    session_id: int
    suggestion_id: int | None
    action_id: int | None
    reaction: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
