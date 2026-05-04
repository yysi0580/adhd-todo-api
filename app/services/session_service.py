from sqlalchemy.orm import Session as DbSession

from app.models import BrainDump, Feedback, Session
from app.repositories.action_repository import ActionRepository
from app.repositories.brain_dump_repository import BrainDumpRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.session_repository import SessionRepository
from app.services.common import require_session


class SessionService:
    def __init__(self, db: DbSession):
        self.db = db
        self.sessions = SessionRepository(db)

    def create(self, user_id: int, context_note: str | None = None) -> Session:
        session = self.sessions.create(user_id=user_id, context_note=context_note)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get(self, user_id: int, session_id: int) -> Session:
        return require_session(self.db, user_id=user_id, session_id=session_id)

    def list_brain_dumps(self, user_id: int, session_id: int) -> list[BrainDump]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        return BrainDumpRepository(self.db).list_by_session(user_id=user_id, session_id=session_id)

    def list_actions(self, user_id: int, session_id: int):
        require_session(self.db, user_id=user_id, session_id=session_id)
        return ActionRepository(self.db).list_by_session(user_id=user_id, session_id=session_id)

    def list_feedback(self, user_id: int, session_id: int) -> list[Feedback]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        return FeedbackRepository(self.db).list_by_session(user_id=user_id, session_id=session_id)
