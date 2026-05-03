from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FeedbackType


class FeedbackCreate(BaseModel):
    session_id: int
    suggestion_id: int
    action_id: int | None = None
    reaction: FeedbackType
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
