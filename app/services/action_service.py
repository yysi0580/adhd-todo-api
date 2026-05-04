from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import (
    DuplicateActionError,
    InvalidStateTransitionError,
    ValidationDomainError,
)
from app.domain.enums import ActionStatus
from app.domain.time import utc_now
from app.models import Action
from app.repositories.action_repository import ActionRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_action, require_session, require_suggestion


class ActionService:
    def __init__(self, db: DbSession):
        self.db = db
        self.actions = ActionRepository(db)
        self.suggestions = SuggestionRepository(db)

    def create(
        self,
        user_id: int,
        session_id: int,
        suggestion_id: int | None,
        title: str | None,
        micro_step: str | None,
    ) -> Action:
        require_session(self.db, user_id=user_id, session_id=session_id)
        suggestion = (
            require_suggestion(self.db, user_id=user_id, suggestion_id=suggestion_id)
            if suggestion_id
            else None
        )
        if suggestion and suggestion.session_id != session_id:
            raise ValidationDomainError(
                "제안이 해당 세션에 속하지 않습니다.",
                code="SUGGESTION_SESSION_MISMATCH",
            )
        if suggestion_id and self.actions.find_by_suggestion_for_user(suggestion_id, user_id):
            raise DuplicateActionError(
                "이미 이 제안으로 생성된 액션이 있습니다.",
                code="DUPLICATE_ACTION_FOR_SUGGESTION",
            )

        resolved_title = title or (suggestion.title if suggestion else None)
        resolved_micro_step = micro_step or (suggestion.micro_step if suggestion else None)
        if not resolved_title or not resolved_micro_step:
            raise ValidationDomainError(
                "suggestion_id 없이 생성하려면 title과 micro_step이 필요합니다.",
                code="ACTION_TEXT_REQUIRED",
            )

        action = self.actions.create(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
            title=resolved_title,
            micro_step=resolved_micro_step,
        )
        self.db.commit()
        self.db.refresh(action)
        return action

    def set_status(self, user_id: int, action_id: int, status: ActionStatus | str) -> Action:
        normalized_status = status.value if isinstance(status, ActionStatus) else status
        action = self._apply_status(user_id, action_id, normalized_status)
        self.db.commit()
        self.db.refresh(action)
        return action

    def complete(self, user_id: int, action_id: int, note: str | None = None) -> Action:
        action = self._apply_status(user_id, action_id, ActionStatus.completed.value)
        action.completion_note = note
        self.db.commit()
        self.db.refresh(action)
        return action

    def abort(self, user_id: int, action_id: int, reason: str | None = None) -> Action:
        action = self._apply_status(user_id, action_id, ActionStatus.aborted.value)
        action.abort_reason = reason
        self.db.commit()
        self.db.refresh(action)
        return action

    def _apply_status(self, user_id: int, action_id: int, status: str) -> Action:
        action = require_action(self.db, user_id=user_id, action_id=action_id)
        if action.status in {ActionStatus.completed.value, ActionStatus.aborted.value}:
            raise InvalidStateTransitionError(
                "이미 종료된 액션은 다시 변경할 수 없습니다.",
                code="ACTION_ALREADY_FINISHED",
            )

        action.status = status
        action.updated_at = utc_now()
        return action
