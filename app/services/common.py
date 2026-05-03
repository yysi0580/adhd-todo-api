from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import not_found
from app.models import Session
from app.repositories.session_repository import SessionRepository


def require_session(db: DbSession, session_id: int) -> Session:
    session = SessionRepository(db).get(session_id)
    if session is None:
        raise not_found("Session not found")
    return session
