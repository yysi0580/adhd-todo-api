from datetime import datetime
from typing import Literal

from pydantic import BaseModel

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
