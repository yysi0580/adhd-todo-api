from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.models import Feedback
from app.repositories.action_repo import ActionRepository
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.suggestion_repo import SuggestionRepository
from app.services.common import require_session


class FeedbackService:
    def __init__(self, db: DbSession):
        self.db = db
        self.actions = ActionRepository(db)
        self.feedback = FeedbackRepository(db)
        self.suggestions = SuggestionRepository(db)

    def create(
        self,
        session_id: int,
        suggestion_id: int | None,
        action_id: int | None,
        reaction: str,
        note: str | None,
    ) -> Feedback:
        require_session(self.db, session_id)
        if suggestion_id is None and action_id is None:
            raise HTTPException(
                status_code=400,
                detail="Either suggestion_id or action_id is required",
            )

        self._validate_suggestion(session_id, suggestion_id)
        self._validate_action(session_id, action_id)

        feedback = self.feedback.create(
            session_id=session_id,
            suggestion_id=suggestion_id,
            action_id=action_id,
            reaction=reaction,
            note=note,
        )
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def _validate_suggestion(self, session_id: int, suggestion_id: int | None) -> None:
        if suggestion_id is None:
            return

        suggestion = self.suggestions.get(suggestion_id)
        if suggestion is None:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        if suggestion.session_id != session_id:
            raise HTTPException(
                status_code=400,
                detail="Suggestion does not belong to this session",
            )

    def _validate_action(self, session_id: int, action_id: int | None) -> None:
        if action_id is None:
            return

        action = self.actions.get(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")
        if action.session_id != session_id:
            raise HTTPException(
                status_code=400,
                detail="Action does not belong to this session",
            )
