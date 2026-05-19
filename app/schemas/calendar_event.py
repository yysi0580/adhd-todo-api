from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class CalendarEventCreate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1200)
    start_at: datetime
    end_at: datetime
    timezone: str = Field(default="Asia/Seoul", min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=255)
    session_id: int | None = None
    action_id: int | None = None
    source: str = Field(default="manual", max_length=40)

    @field_validator("title", "description", "timezone", "location", "source", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_time_range(self) -> "CalendarEventCreate":
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at.")
        return self


class CalendarEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=1200)
    start_at: datetime | None = None
    end_at: datetime | None = None
    timezone: str | None = Field(default=None, min_length=1, max_length=80)
    location: str | None = Field(default=None, max_length=255)

    @field_validator("title", "description", "timezone", "location", mode="before")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CalendarEventRead(BaseModel):
    id: int
    user_id: int
    session_id: int | None
    action_id: int | None
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime
    timezone: str
    location: str | None
    source: str
    external_uid: str | None
    provider: str | None
    external_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
