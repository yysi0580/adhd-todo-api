from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

EffortLevel = Literal["quiet", "gentle", "neutral"]


class RoutineCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    micro_step: str = Field(min_length=1, max_length=500)
    effort_level: EffortLevel = "quiet"
    is_active: bool = True

    @field_validator("title", "micro_step", mode="before")
    @classmethod
    def trim_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("값을 입력해주세요.")
        return normalized


class RoutineUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    micro_step: str | None = Field(default=None, min_length=1, max_length=500)
    effort_level: EffortLevel | None = None
    is_active: bool | None = None

    @field_validator("title", "micro_step", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("값을 입력해주세요.")
        return normalized


class RoutineRead(BaseModel):
    id: int
    user_id: int
    title: str
    micro_step: str
    effort_level: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
