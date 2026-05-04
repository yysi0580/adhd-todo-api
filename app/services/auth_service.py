from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.core.exceptions import ValidationDomainError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: DbSession):
        self.db = db
        self.users = UserRepository(db)

    def register(self, email: str, password: str) -> User:
        if self.users.get_by_email(email):
            raise ValidationDomainError(
                "이미 가입된 이메일입니다.",
                code="EMAIL_ALREADY_REGISTERED",
            )

        user = self.users.create(email=email, password_hash=hash_password(password))
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValidationDomainError(
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                code="INVALID_LOGIN",
            )

        settings = get_settings()
        return create_access_token(
            subject=str(user.id),
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
