from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    context_note: str | None = None


class SessionRead(BaseModel):
    id: int
    user_id: int | None
    context_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
