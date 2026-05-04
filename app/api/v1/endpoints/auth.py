from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, db: DbSession = Depends(get_db)):
    return AuthService(db).register(email=payload.email, password=payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession = Depends(get_db)):
    token = AuthService(db).login(email=payload.email, password=payload.password)
    return {"access_token": token, "token_type": "bearer"}
