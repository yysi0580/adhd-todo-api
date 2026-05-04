from sqlalchemy.orm import Session as DbSession

from app.models import User


class UserRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create(self, email: str, password_hash: str, nickname: str | None = None) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            nickname=nickname,
        )
        self.db.add(user)
        self.db.flush()
        return user
