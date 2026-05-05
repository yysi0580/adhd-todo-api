from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import ValidationDomainError
from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: DbSession):
        self.db = db
        self.users = UserRepository(db)

    def update_me(self, user: User, nickname: str) -> User:
        updated = self.users.update_nickname(user, nickname=nickname)
        self.db.commit()
        self.db.refresh(updated)
        return updated

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.password_hash):
            raise ValidationDomainError(
                "현재 비밀번호가 올바르지 않습니다.",
                code="INVALID_CURRENT_PASSWORD",
            )
        self._validate_password(new_password)
        user.password_hash = hash_password(new_password)
        self.db.commit()

    def _validate_password(self, password: str) -> None:
        has_letter = any(character.isalpha() for character in password)
        has_digit = any(character.isdigit() for character in password)
        if len(password) < 8 or not has_letter or not has_digit:
            raise ValidationDomainError(
                "비밀번호는 8자 이상이며 문자와 숫자를 포함해야 합니다.",
                code="WEAK_PASSWORD",
            )
