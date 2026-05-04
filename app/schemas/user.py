from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: int
    email: EmailStr
    nickname: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
