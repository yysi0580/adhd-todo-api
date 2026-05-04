from sqlalchemy.orm import Session as DbSession

from app.domain.enums import SuggestionGenerationType
from app.models import Suggestion
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session, require_suggestion
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
        suggestion = require_suggestion(self.db, user_id=user_id, suggestion_id=suggestion_id)

        items = (
            self.generator.make_smaller(suggestion.title, suggestion.micro_step)
            if hasattr(self.generator, "make_smaller")
            else self.generator.generate_smaller_steps(suggestion.micro_step)
        )

        new_suggestions = self.suggestions.create_many(
            user_id=user_id,
            session_id=suggestion.session_id,
            brain_dump_id=suggestion.brain_dump_id,
            items=items,
            parent_suggestion_id=suggestion.id,
        )
        for new_suggestion in new_suggestions:
            new_suggestion.generation_type = SuggestionGenerationType.smaller.value
        self.db.commit()
        for new_suggestion in new_suggestions:
            self.db.refresh(new_suggestion)
        return new_suggestions
