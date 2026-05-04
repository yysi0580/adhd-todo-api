from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError
from app.domain.enums import SuggestionGenerationType
from app.models import Suggestion
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session
from app.services.suggestion.generator import SuggestionGenerator


class SuggestionService:
    def __init__(self, db: DbSession, generator: SuggestionGenerator):
        self.db = db
        self.generator = generator
        self.suggestions = SuggestionRepository(db)

    def list_by_session(self, user_id: int, session_id: int) -> list[Suggestion]:
        require_session(self.db, user_id=user_id, session_id=session_id)
        return self.suggestions.list_by_session(user_id=user_id, session_id=session_id)

    def make_smaller(self, user_id: int, suggestion_id: int) -> list[Suggestion]:
        suggestion = self.suggestions.get_for_user(suggestion_id=suggestion_id, user_id=user_id)
        if suggestion is None:
            raise NotFoundError("제안을 찾을 수 없습니다.", code="SUGGESTION_NOT_FOUND")

        new_suggestions = self.suggestions.create_many(
            user_id=user_id,
            session_id=suggestion.session_id,
            brain_dump_id=suggestion.brain_dump_id,
            items=self.generator.generate_smaller_steps(suggestion.micro_step),
            parent_suggestion_id=suggestion.id,
        )
        for new_suggestion in new_suggestions:
            new_suggestion.generation_type = SuggestionGenerationType.smaller.value
        self.db.commit()
        for new_suggestion in new_suggestions:
            self.db.refresh(new_suggestion)
        return new_suggestions
