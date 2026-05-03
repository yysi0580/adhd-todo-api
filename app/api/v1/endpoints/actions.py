from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.action import ActionAbort, ActionComplete, ActionCreate, ActionRead, ActionUpdate
from app.services.action_service import ActionService

router = APIRouter()


@router.post("", response_model=ActionRead, status_code=201)
def create_action(payload: ActionCreate, db: DbSession = Depends(get_db)):
    return ActionService(db).create(
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        title=payload.title,
        micro_step=payload.micro_step,
    )


@router.patch("/{action_id}", response_model=ActionRead)
def update_action(action_id: int, payload: ActionUpdate, db: DbSession = Depends(get_db)):
    return ActionService(db).set_status(action_id, payload.status.value)


@router.post("/{action_id}/complete", response_model=ActionRead)
def complete_action(
    action_id: int,
    payload: ActionComplete | None = None,
    db: DbSession = Depends(get_db),
):
    note = payload.note if payload else None
    return ActionService(db).complete(action_id, note=note)


@router.post("/{action_id}/abort", response_model=ActionRead)
def abort_action(
    action_id: int,
    payload: ActionAbort | None = None,
    db: DbSession = Depends(get_db),
):
    reason = payload.reason if payload else None
    return ActionService(db).abort(action_id, reason=reason)
