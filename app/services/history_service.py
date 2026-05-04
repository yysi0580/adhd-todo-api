from sqlalchemy.orm import Session as DbSession

from app.repositories.action_repository import ActionRepository
from app.repositories.brain_dump_repository import BrainDumpRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.session_repository import SessionRepository


class HistoryService:
    def __init__(self, db: DbSession):
        self.db = db

    def read_recent(self, user_id: int, limit: int = 20) -> dict:
        return {
            "sessions": SessionRepository(self.db).list_recent_for_user(user_id, limit),
            "brain_dumps": BrainDumpRepository(self.db).list_recent_for_user(user_id, limit),
            "actions": ActionRepository(self.db).list_recent_for_user(user_id, limit),
            "feedback": FeedbackRepository(self.db).list_recent_for_user(user_id, limit),
        }
