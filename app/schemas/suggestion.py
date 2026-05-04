from datetime import datetime

from pydantic import BaseModel


class SuggestionRead(BaseModel):
    id: int
    user_id: int | None
    session_id: int
    brain_dump_id: int | None
    parent_suggestion_id: int | None
    generation_type: str
    source: str
    title: str
    micro_step: str
    effort_level: str
    created_at: datetime

    model_config = {"from_attributes": True}
