from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError
from app.models import Session
from app.repositories.session_repository import SessionRepository


def require_session(db: DbSession, user_id: int, session_id: int) -> Session:
    session = SessionRepository(db).get_for_user(session_id=session_id, user_id=user_id)
    if session is None:
        raise NotFoundError("세션을 찾을 수 없습니다.", code="SESSION_NOT_FOUND")
    return session
