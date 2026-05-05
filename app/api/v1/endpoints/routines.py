from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.action import ActionRead
from app.schemas.routine import RoutineCreate, RoutineRead, RoutineUpdate
from app.services.routine_service import RoutineService

router = APIRouter()


@router.get("", response_model=list[RoutineRead])
def list_routines(
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoutineService(db).list(current_user.id)


@router.post("", response_model=RoutineRead, status_code=201)
def create_routine(
    payload: RoutineCreate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoutineService(db).create(
        user_id=current_user.id,
        title=payload.title,
        micro_step=payload.micro_step,
        effort_level=payload.effort_level,
        is_active=payload.is_active,
    )


@router.patch("/{routine_id}", response_model=RoutineRead)
def update_routine(
    routine_id: int,
    payload: RoutineUpdate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoutineService(db).update(
        user_id=current_user.id,
        routine_id=routine_id,
        title=payload.title,
        micro_step=payload.micro_step,
        effort_level=payload.effort_level,
        is_active=payload.is_active,
    )


@router.delete("/{routine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine(
    routine_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    RoutineService(db).delete(current_user.id, routine_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{routine_id}/start-action", response_model=ActionRead, status_code=201)
def start_routine_action(
    routine_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return RoutineService(db).start_action(current_user.id, routine_id)
