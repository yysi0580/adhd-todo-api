from sqlalchemy.orm import Session as DbSession

from app.models import Action


class ActionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, action_id: int) -> Action | None:
        return self.db.get(Action, action_id)

    def get_for_user(self, action_id: int, user_id: int) -> Action | None:
        return (
            self.db.query(Action).filter(Action.id == action_id, Action.user_id == user_id).first()
        )

    def find_by_suggestion_for_user(self, suggestion_id: int, user_id: int) -> Action | None:
        return (
            self.db.query(Action)
            .filter(Action.suggestion_id == suggestion_id, Action.user_id == user_id)
            .first()
        )

    def list_by_session(self, user_id: int, session_id: int) -> list[Action]:
        return (
            self.db.query(Action)
            .filter(Action.user_id == user_id, Action.session_id == session_id)
            .order_by(Action.created_at.desc())
            .all()
        )

    def list_recent_for_user(self, user_id: int, limit: int = 20) -> list[Action]:
        return (
            self.db.query(Action)
            .filter(Action.user_id == user_id)
            .order_by(Action.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(
        self,
        user_id: int,
        session_id: int,
        suggestion_id: int | None,
        title: str,
        micro_step: str,
    ) -> Action:
        action = Action(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
            title=title,
            micro_step=micro_step,
        )
        self.db.add(action)
        self.db.flush()
        return action
