from sqlalchemy.orm import Session as DbSession

from app.models import Action


class ActionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, action_id: int) -> Action | None:
        return self.db.get(Action, action_id)

    def create(
        self,
        session_id: int,
        suggestion_id: int | None,
        title: str,
        micro_step: str,
    ) -> Action:
        action = Action(
            session_id=session_id,
            suggestion_id=suggestion_id,
            title=title,
            micro_step=micro_step,
        )
        self.db.add(action)
        self.db.flush()
        return action
