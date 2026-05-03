from fastapi import HTTPException
from sqlalchemy.orm import Session as DbSession

from app.domain.enums import ActionStatus
from app.domain.time import utc_now
from app.models import Action
from app.repositories.action_repository import ActionRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session


class ActionService:
    def __init__(self, db: DbSession):
        self.db = db
        self.actions = ActionRepository(db)
        self.suggestions = SuggestionRepository(db)

    def create(
        self,
        session_id: int,
        suggestion_id: int | None,
        title: str | None,
        micro_step: str | None,
    ) -> Action:
        require_session(self.db, session_id)
        suggestion = self.suggestions.get(suggestion_id) if suggestion_id else None
        if suggestion_id and suggestion is None:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        if suggestion and suggestion.session_id != session_id:
            raise HTTPException(
                status_code=400,
                detail="Suggestion does not belong to this session",
            )

        resolved_title = title or (suggestion.title if suggestion else None)
        resolved_micro_step = micro_step or (suggestion.micro_step if suggestion else None)
        if not resolved_title or not resolved_micro_step:
            raise HTTPException(
                status_code=400,
                detail="title and micro_step are required without suggestion_id",
            )

        action = self.actions.create(
            session_id=session_id,
            suggestion_id=suggestion_id,
            title=resolved_title,
            micro_step=resolved_micro_step,
        )
        self.db.commit()
        self.db.refresh(action)
        return action

    def set_status(self, action_id: int, status: ActionStatus | str) -> Action:
        action = self.actions.get(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")

        action.status = status.value if isinstance(status, ActionStatus) else status
        action.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(action)
        return action
