from sqlalchemy.orm import Session as DbSession

from app.models import Feedback


class FeedbackRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def create(
        self,
        user_id: int,
        session_id: int,
        suggestion_id: int | None,
        action_id: int | None,
        reaction: str,
        note: str | None,
    ) -> Feedback:
        feedback = Feedback(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
            action_id=action_id,
            reaction=reaction,
            note=note,
        )
        self.db.add(feedback)
        self.db.flush()
        return feedback

    def list_by_session(self, user_id: int, session_id: int) -> list[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id, Feedback.session_id == session_id)
            .order_by(Feedback.created_at.desc())
            .all()
        )

    def list_recent_for_user(self, user_id: int, limit: int = 20) -> list[Feedback]:
        return (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.created_at.desc())
            .limit(limit)
            .all()
        )
