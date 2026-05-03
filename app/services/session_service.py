from sqlalchemy.orm import Session as DbSession

from app.models import Session
from app.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, db: DbSession):
        self.db = db
        self.sessions = SessionRepository(db)

    def create(self, context_note: str | None = None) -> Session:
        session = self.sessions.create(context_note=context_note)
        self.db.commit()
        self.db.refresh(session)
        return session
