from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import bad_request, not_found
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
            raise not_found("Suggestion not found")
        if suggestion and suggestion.session_id != session_id:
            raise bad_request("Suggestion does not belong to this session")

        resolved_title = title or (suggestion.title if suggestion else None)
        resolved_micro_step = micro_step or (suggestion.micro_step if suggestion else None)
        if not resolved_title or not resolved_micro_step:
            raise bad_request("title and micro_step are required without suggestion_id")

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
        normalized_status = status.value if isinstance(status, ActionStatus) else status
        return self._finalize(action_id, normalized_status)

    def complete(self, action_id: int, note: str | None = None) -> Action:
        action = self._finalize(action_id, ActionStatus.completed.value)
        action.completion_note = note
        self.db.commit()
        self.db.refresh(action)
        return action

    def abort(self, action_id: int, reason: str | None = None) -> Action:
        action = self._finalize(action_id, ActionStatus.aborted.value)
        action.abort_reason = reason
        self.db.commit()
        self.db.refresh(action)
        return action

    def _finalize(self, action_id: int, status: str) -> Action:
        action = self.actions.get(action_id)
        if action is None:
            raise not_found("Action not found")
        if action.status in {ActionStatus.completed.value, ActionStatus.aborted.value}:
            raise bad_request("Action is already finished")

        action.status = status
        action.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(action)
        return action
