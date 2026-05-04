from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.action import ActionRead
from app.schemas.brain_dump import BrainDumpRead
from app.schemas.feedback import FeedbackRead
from app.schemas.session import SessionCreate, SessionRead
from app.services.session_service import SessionService

router = APIRouter()


@router.post("", response_model=SessionRead, status_code=201)
def create_session(
    payload: SessionCreate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService(db).create(user_id=current_user.id, context_note=payload.context_note)


@router.get("/{session_id}", response_model=SessionRead)
def read_session(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService(db).get(user_id=current_user.id, session_id=session_id)


@router.get("/{session_id}/brain-dumps", response_model=list[BrainDumpRead])
def list_session_brain_dumps(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService(db).list_brain_dumps(user_id=current_user.id, session_id=session_id)


@router.get("/{session_id}/actions", response_model=list[ActionRead])
def list_session_actions(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService(db).list_actions(user_id=current_user.id, session_id=session_id)


@router.get("/{session_id}/feedback", response_model=list[FeedbackRead])
def list_session_feedback(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SessionService(db).list_feedback(user_id=current_user.id, session_id=session_id)
