from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import client_ip, enforce_rate_limit
from app.core.config import get_settings
from app.core.db import get_db
from app.core.exceptions import ValidationDomainError
from app.core.limits import clear_login_failures, is_login_blocked, record_login_failure
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, db: DbSession = Depends(get_db)):
    return AuthService(db).register(email=payload.email, password=payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: DbSession = Depends(get_db)):
    settings = get_settings()
    ip = client_ip(request)
    rate_key = f"login:rate:{ip}:{payload.email.lower()}"
    block_key = f"login:block:{ip}:{payload.email.lower()}"
    enforce_rate_limit(rate_key, limit=settings.login_rate_limit_per_minute)
    if is_login_blocked(block_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": "LOGIN_BLOCKED",
                "message": "로그인 실패가 반복되어 잠시 차단되었습니다.",
            },
        )

    try:
        tokens = AuthService(db).login(email=payload.email, password=payload.password)
    except ValidationDomainError:
        record_login_failure(
            block_key,
            limit=settings.login_failure_limit,
            block_minutes=settings.login_block_minutes,
        )
        raise

    clear_login_failures(block_key)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: DbSession = Depends(get_db)):
    return AuthService(db).refresh(refresh_token=payload.refresh_token)
