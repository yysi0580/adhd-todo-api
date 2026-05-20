from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.domain.enums import (
    CalendarCandidateStatus,
    CalendarCandidateType,
    CalendarEnergyLevel,
    CalendarFrictionLevel,
    CalendarPreferredTimeBlock,
    CalendarSplitStrategy,
)
from app.schemas.calendar_event import CalendarEventRead


class CalendarCandidateFromSuggestions(BaseModel):
    session_id: int
    suggestion_ids: list[int] | None = Field(default=None, max_length=10)


class CalendarCandidateSchedule(BaseModel):
    start_at: datetime
    end_at: datetime
    timezone: str = Field(default="Asia/Seoul", min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=255)

    @field_validator("timezone", "location", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_time_range(self) -> "CalendarCandidateSchedule":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at.")
        return self


class CalendarCandidateRead(BaseModel):
    id: int
    user_id: int
    session_id: int
    suggestion_id: int | None
    action_id: int | None
    title: str
    micro_step: str
    candidate_type: CalendarCandidateType
    estimated_minutes: int
    min_minutes: int
    max_minutes: int
    preferred_date: datetime | None
    earliest_start_at: datetime | None
    latest_end_at: datetime | None
    due_at: datetime | None
    preferred_time_block: CalendarPreferredTimeBlock
    energy_level: CalendarEnergyLevel
    friction_level: CalendarFrictionLevel
    split_strategy: CalendarSplitStrategy
    status: CalendarCandidateStatus
    reason: str | None
    timezone: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CalendarCandidateScheduleResponse(BaseModel):
    candidate: CalendarCandidateRead
    event: CalendarEventRead
