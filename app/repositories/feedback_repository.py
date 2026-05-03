from sqlalchemy.orm import Session as DbSession

from app.models import Feedback


class FeedbackRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def create(
        self,
        session_id: int,
        suggestion_id: int | None,
        action_id: int | None,
        reaction: str,
        note: str | None,
    ) -> Feedback:
        feedback = Feedback(
            session_id=session_id,
            suggestion_id=suggestion_id,
            action_id=action_id,
            reaction=reaction,
            note=note,
        )
        self.db.add(feedback)
        self.db.flush()
        return feedback
