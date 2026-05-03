from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import not_found
from app.models import Suggestion
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session
from app.services.suggestion.generator import SuggestionGenerator


class SuggestionService:
    def __init__(self, db: DbSession, generator: SuggestionGenerator):
        self.db = db
        self.generator = generator
        self.suggestions = SuggestionRepository(db)

    def list_by_session(self, session_id: int) -> list[Suggestion]:
        require_session(self.db, session_id)
        return self.suggestions.list_by_session(session_id)

    def make_smaller(self, suggestion_id: int) -> list[Suggestion]:
        suggestion = self.suggestions.get(suggestion_id)
        if suggestion is None:
            raise not_found("Suggestion not found")

        new_suggestions = self.suggestions.create_many(
            session_id=suggestion.session_id,
            brain_dump_id=suggestion.brain_dump_id,
            items=self.generator.generate_smaller_steps(suggestion.micro_step),
        )
        self.db.commit()
        for new_suggestion in new_suggestions:
            self.db.refresh(new_suggestion)
        return new_suggestions
