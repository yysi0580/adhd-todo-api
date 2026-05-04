from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import FeedbackType
from app.schemas.suggestion import SuggestionRead


class FeedbackCreate(BaseModel):
    session_id: int
    suggestion_id: int
    action_id: int | None = None
    reaction: FeedbackType
    note: str | None = None


class FeedbackRead(BaseModel):
    id: int
    user_id: int | None
    session_id: int
    suggestion_id: int | None
    action_id: int | None
    reaction: str
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class FeedbackResponse(BaseModel):
    feedback: FeedbackRead
    action_id: int | None = None
    smaller_suggestions: list[SuggestionRead] = []
