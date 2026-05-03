from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models import Session
from app.repositories.session_repo import SessionRepository


def require_session(db: DbSession, session_id: int) -> Session:
    session = SessionRepository(db).get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
