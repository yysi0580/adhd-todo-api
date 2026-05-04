from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.core.exceptions import ValidationDomainError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: DbSession):
        self.db = db
        self.users = UserRepository(db)

    def register(self, email: str, password: str, nickname: str | None = None) -> User:
        self._validate_password(password)
        if self.users.get_by_email(email):
            raise ValidationDomainError(
                "이미 가입된 이메일입니다.",
                code="EMAIL_ALREADY_REGISTERED",
            )

        user = self.users.create(
            email=email,
            password_hash=hash_password(password),
            nickname=nickname,
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> dict[str, str]:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValidationDomainError(
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                code="INVALID_LOGIN",
            )

        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_refresh_token(refresh_token)
            user_id = int(payload.get("sub", ""))
        except Exception as exc:
            raise ValidationDomainError(
                "refresh token이 올바르지 않습니다.",
                code="INVALID_REFRESH_TOKEN",
            ) from exc

        user = self.users.get(user_id)
        if user is None:
            raise ValidationDomainError(
                "refresh token이 올바르지 않습니다.",
                code="INVALID_REFRESH_TOKEN",
            )
        return self._issue_tokens(user)

    def _issue_tokens(self, user: User) -> dict[str, str]:
        settings = get_settings()
        return {
            "access_token": create_access_token(
                subject=str(user.id),
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
            ),
            "refresh_token": create_refresh_token(
                subject=str(user.id),
                expires_delta=timedelta(days=settings.refresh_token_expire_days),
            ),
            "token_type": "bearer",
        }

    def _validate_password(self, password: str) -> None:
        has_letter = any(character.isalpha() for character in password)
        has_digit = any(character.isdigit() for character in password)
        if len(password) < 8 or not has_letter or not has_digit:
            raise ValidationDomainError(
                "비밀번호는 8자 이상이며 문자와 숫자를 포함해야 합니다.",
                code="WEAK_PASSWORD",
            )
