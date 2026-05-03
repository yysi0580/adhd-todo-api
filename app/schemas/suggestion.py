from datetime import datetime

from pydantic import BaseModel


class SuggestionRead(BaseModel):
    id: int
    session_id: int
    brain_dump_id: int | None
    title: str
    micro_step: str
    effort_level: str
    created_at: datetime

    model_config = {"from_attributes": True}
