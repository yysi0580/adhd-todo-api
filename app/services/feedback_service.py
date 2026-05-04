from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError, ValidationDomainError
from app.domain.enums import FeedbackType, SuggestionGenerationType
from app.models import Feedback, Suggestion
from app.repositories.action_repository import ActionRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session
from app.services.suggestion import SuggestionGenerator


class FeedbackService:
    def __init__(self, db: DbSession, generator: SuggestionGenerator | None = None):
        self.db = db
        self.generator = generator
        self.actions = ActionRepository(db)
        self.feedback = FeedbackRepository(db)
        self.suggestions = SuggestionRepository(db)

    def create(
        self,
        user_id: int,
        session_id: int,
        suggestion_id: int,
        action_id: int | None,
        reaction: str,
        note: str | None,
    ) -> tuple[Feedback, list[Suggestion]]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        suggestion = self._get_suggestion(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
        )
        self._validate_action(user_id=user_id, session_id=session_id, action_id=action_id)

        smaller_suggestions: list[Suggestion] = []
        resolved_action_id = action_id

        if reaction == FeedbackType.do.value:
            action = self.actions.find_by_suggestion_for_user(
                suggestion_id=suggestion_id,
                user_id=user_id,
            )
            if action is None:
                action = self.actions.create(
                    user_id=user_id,
                    session_id=session_id,
                    suggestion_id=suggestion_id,
                    title=suggestion.title,
                    micro_step=suggestion.micro_step,
                )
            resolved_action_id = action.id

        if reaction == FeedbackType.make_smaller.value:
            if self.generator is None:
                raise ValidationDomainError(
                    "더 작은 제안을 생성할 수 없습니다.",
                    code="SUGGESTION_GENERATOR_REQUIRED",
                )
            smaller_suggestions = self.suggestions.create_many(
                user_id=user_id,
                session_id=session_id,
                brain_dump_id=suggestion.brain_dump_id,
                parent_suggestion_id=suggestion.id,
                items=[
                    {
                        **item,
                        "generation_type": SuggestionGenerationType.smaller.value,
                    }
                    for item in self.generator.generate_smaller_steps(suggestion.micro_step)
                ],
            )

        feedback = self.feedback.create(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
            action_id=resolved_action_id,
            reaction=reaction,
            note=note,
        )
        self.db.commit()
        self.db.refresh(feedback)
        for smaller_suggestion in smaller_suggestions:
            self.db.refresh(smaller_suggestion)
        return feedback, smaller_suggestions

    def _get_suggestion(self, user_id: int, session_id: int, suggestion_id: int) -> Suggestion:
        suggestion = self.suggestions.get_for_user(suggestion_id=suggestion_id, user_id=user_id)
        if suggestion is None:
            raise NotFoundError("제안을 찾을 수 없습니다.", code="SUGGESTION_NOT_FOUND")
        if suggestion.session_id != session_id:
            raise ValidationDomainError(
                "제안이 해당 세션에 속하지 않습니다.",
                code="SUGGESTION_SESSION_MISMATCH",
            )
        return suggestion

    def _validate_action(self, user_id: int, session_id: int, action_id: int | None) -> None:
        if action_id is None:
            return

        action = self.actions.get_for_user(action_id=action_id, user_id=user_id)
        if action is None:
            raise NotFoundError("액션을 찾을 수 없습니다.", code="ACTION_NOT_FOUND")
        if action.session_id != session_id:
            raise ValidationDomainError(
                "액션이 해당 세션에 속하지 않습니다.",
                code="ACTION_SESSION_MISMATCH",
            )
