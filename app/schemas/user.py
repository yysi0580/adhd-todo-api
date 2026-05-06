from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRead(BaseModel):
    id: int
    email: EmailStr
    nickname: str | None = None
    email_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: str = Field(min_length=2, max_length=30)

    @field_validator("nickname", mode="before")
    @classmethod
    def normalize_nickname(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("닉네임을 입력해주세요.")
        return normalized


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
