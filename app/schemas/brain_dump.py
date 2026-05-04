from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.session import SessionRead
from app.schemas.suggestion import SuggestionRead


class BrainDumpCreate(BaseModel):
    session_id: int | None = None
    raw_text: str = Field(min_length=1, max_length=5000)


class BrainDumpRead(BaseModel):
    id: int
    user_id: int | None
    session_id: int
    raw_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class BrainDumpResponse(BaseModel):
    session: SessionRead
    brain_dump: BrainDumpRead
    suggestions: list[SuggestionRead]
