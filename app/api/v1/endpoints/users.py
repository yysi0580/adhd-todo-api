from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.user import MessageResponse, PasswordChangeRequest, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(
    payload: UserUpdate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService(db).update_me(current_user, nickname=payload.nickname)


@router.patch("/me/password", response_model=MessageResponse)
def change_my_password(
    payload: PasswordChangeRequest,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    UserService(db).change_password(
        current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"message": "비밀번호가 변경되었습니다."}
