from sqlalchemy.orm import Session as DbSession

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
