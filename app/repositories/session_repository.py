from sqlalchemy.orm import Session as DbSession

from app.models import Session


class SessionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, session_id: int) -> Session | None:
        return self.db.get(Session, session_id)

    def get_for_user(self, session_id: int, user_id: int) -> Session | None:
        return (
            self.db.query(Session)
            .filter(Session.id == session_id, Session.user_id == user_id)
            .first()
        )

    def list_recent_for_user(self, user_id: int, limit: int = 20) -> list[Session]:
        return (
            self.db.query(Session)
            .filter(Session.user_id == user_id)
            .order_by(Session.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, user_id: int, context_note: str | None = None) -> Session:
        session = Session(user_id=user_id, context_note=context_note)
        self.db.add(session)
        self.db.flush()
        return session
