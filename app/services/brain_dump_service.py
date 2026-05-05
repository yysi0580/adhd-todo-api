from sqlalchemy.orm import Session as DbSession

from app.models import BrainDump, Session, Suggestion
from app.repositories.brain_dump_repository import BrainDumpRepository
from app.repositories.routine_repository import RoutineRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.suggestion_repository import SuggestionRepository
from app.services.common import require_session
from app.services.suggestion.generator import SuggestionGenerator


class BrainDumpService:
    def __init__(self, db: DbSession, generator: SuggestionGenerator):
        self.db = db
        self.generator = generator
        self.sessions = SessionRepository(db)
        self.brain_dumps = BrainDumpRepository(db)
        self.suggestions = SuggestionRepository(db)
        self.routines = RoutineRepository(db)

    def create_with_suggestions(
        self,
        user_id: int,
        raw_text: str,
        session_id: int | None = None,
    ) -> tuple[Session, BrainDump, list[Suggestion]]:
        session = self._get_or_create_session(user_id=user_id, session_id=session_id)
        brain_dump = self.brain_dumps.create(
            user_id=user_id,
            session_id=session.id,
            raw_text=raw_text,
        )
        generated_items = self._with_routine_safety_net(
            user_id=user_id,
            items=self.generator.generate_micro_steps(raw_text, user_id=user_id),
        )
        suggestions = self.suggestions.create_many(
            user_id=user_id,
            session_id=session.id,
            brain_dump_id=brain_dump.id,
            items=generated_items,
        )
        self.db.commit()
        self.db.refresh(session)
        self.db.refresh(brain_dump)
        for suggestion in suggestions:
            self.db.refresh(suggestion)
        return session, brain_dump, suggestions

    def _get_or_create_session(self, user_id: int, session_id: int | None) -> Session:
        if session_id is None:
            return self.sessions.create(user_id=user_id)

        return require_session(self.db, user_id=user_id, session_id=session_id)

    def _with_routine_safety_net(
        self,
        user_id: int,
        items: list[dict[str, str]],
        limit: int = 5,
    ) -> list[dict[str, str]]:
        if len(items) >= 2:
            return items[:limit]
        routine_items = [
            {
                "title": routine.title,
                "micro_step": routine.micro_step,
                "effort_level": routine.effort_level,
                "generation_type": "safety_net",
                "source": "rule_based",
            }
            for routine in self.routines.list_active_for_user(user_id=user_id, limit=limit)
        ]
        seen_titles = {item.get("title") for item in items}
        for routine_item in routine_items:
            if routine_item["title"] not in seen_titles:
                items.append(routine_item)
            if len(items) >= 2:
                break
        return items[:limit]
