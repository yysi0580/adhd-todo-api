from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models import Routine
from app.repositories.routine_repository import RoutineRepository


class RoutineService:
    def __init__(self, db: DbSession):
        self.db = db
        self.routines = RoutineRepository(db)

    def list(self, user_id: int) -> list[Routine]:
        return self.routines.list_for_user(user_id)

    def create(
        self,
        user_id: int,
        title: str,
        micro_step: str,
        effort_level: str,
        is_active: bool,
    ) -> Routine:
        routine = self.routines.create(
            user_id=user_id,
            title=title,
            micro_step=micro_step,
            effort_level=effort_level,
            is_active=is_active,
        )
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def update(
        self,
        user_id: int,
        routine_id: int,
        title: str | None = None,
        micro_step: str | None = None,
        effort_level: str | None = None,
        is_active: bool | None = None,
    ) -> Routine:
        routine = self._require_owned(user_id, routine_id)
        if title is not None:
            routine.title = title
        if micro_step is not None:
            routine.micro_step = micro_step
        if effort_level is not None:
            routine.effort_level = effort_level
        if is_active is not None:
            routine.is_active = is_active
        self.db.commit()
        self.db.refresh(routine)
        return routine

    def delete(self, user_id: int, routine_id: int) -> None:
        routine = self._require_owned(user_id, routine_id)
        self.routines.delete(routine)
        self.db.commit()

    def _require_owned(self, user_id: int, routine_id: int) -> Routine:
        routine = self.routines.get(routine_id)
        if routine is None:
            raise NotFoundError("루틴을 찾을 수 없습니다.", code="ROUTINE_NOT_FOUND")
        if routine.user_id != user_id:
            raise PermissionDeniedError("루틴 접근 권한이 없습니다.", code="ROUTINE_FORBIDDEN")
        return routine
