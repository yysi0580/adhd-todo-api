from sqlalchemy.orm import Session as DbSession

from app.models import Session


class SessionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, session_id: int) -> Session | None:
        return self.db.get(Session, session_id)

    def create(self, context_note: str | None = None) -> Session:
        session = Session(context_note=context_note)
        self.db.add(session)
        self.db.flush()
        return session
