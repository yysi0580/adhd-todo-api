from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


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
