from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import not_found
from app.models import BrainDump, Session, Suggestion
from app.repositories.brain_dump_repository import BrainDumpRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.suggestion.generator import SuggestionGenerator


class BrainDumpService:
    def __init__(self, db: DbSession, generator: SuggestionGenerator):
        self.db = db
        self.generator = generator
        self.sessions = SessionRepository(db)
        self.brain_dumps = BrainDumpRepository(db)
        self.suggestions = SuggestionRepository(db)

    def create_with_suggestions(
        self,
        raw_text: str,
        session_id: int | None = None,
    ) -> tuple[Session, BrainDump, list[Suggestion]]:
        session = self._get_or_create_session(session_id)
        brain_dump = self.brain_dumps.create(session_id=session.id, raw_text=raw_text)
        suggestions = self.suggestions.create_many(
            session_id=session.id,
            brain_dump_id=brain_dump.id,
            items=self.generator.generate_micro_steps(raw_text),
        )
        self.db.commit()
        self.db.refresh(session)
        self.db.refresh(brain_dump)
        for suggestion in suggestions:
            self.db.refresh(suggestion)
        return session, brain_dump, suggestions

    def _get_or_create_session(self, session_id: int | None) -> Session:
        if session_id is None:
            return self.sessions.create()

        session = self.sessions.get(session_id)
        if session is None:
            raise not_found("Session not found")
        return session
