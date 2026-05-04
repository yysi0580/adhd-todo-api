from sqlalchemy.orm import Session as DbSession

from app.models import Routine


class RoutineRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, routine_id: int) -> Routine | None:
        return self.db.get(Routine, routine_id)

    def list_for_user(self, user_id: int) -> list[Routine]:
        return (
            self.db.query(Routine)
            .filter(Routine.user_id == user_id)
            .order_by(Routine.created_at.desc())
            .all()
        )

    def create(
        self,
        user_id: int,
        title: str,
        micro_step: str,
        effort_level: str,
        is_active: bool,
    ) -> Routine:
        routine = Routine(
            user_id=user_id,
            title=title,
            micro_step=micro_step,
            effort_level=effort_level,
            is_active=is_active,
        )
        self.db.add(routine)
        self.db.flush()
        return routine

    def delete(self, routine: Routine) -> None:
        self.db.delete(routine)
