from sqlalchemy.orm import Session as DbSession

from app.domain.enums import SuggestionGenerationType, SuggestionSource
from app.models import Suggestion


class SuggestionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, suggestion_id: int) -> Suggestion | None:
        return self.db.get(Suggestion, suggestion_id)

    def get_for_user(self, suggestion_id: int, user_id: int) -> Suggestion | None:
        return (
            self.db.query(Suggestion)
            .filter(Suggestion.id == suggestion_id, Suggestion.user_id == user_id)
            .first()
        )

    def list_by_session(self, user_id: int, session_id: int) -> list[Suggestion]:
        return (
            self.db.query(Suggestion)
            .filter(Suggestion.user_id == user_id, Suggestion.session_id == session_id)
            .order_by(Suggestion.created_at.desc())
            .all()
        )

    def create(
        self,
        user_id: int,
        session_id: int,
        brain_dump_id: int | None,
        title: str,
        micro_step: str,
        effort_level: str,
        parent_suggestion_id: int | None = None,
        generation_type: str = SuggestionGenerationType.original.value,
        source: str = SuggestionSource.rule_based.value,
    ) -> Suggestion:
        suggestion = Suggestion(
            user_id=user_id,
            session_id=session_id,
            brain_dump_id=brain_dump_id,
            parent_suggestion_id=parent_suggestion_id,
            generation_type=generation_type,
            source=source,
            title=title,
            micro_step=micro_step,
            effort_level=effort_level,
        )
        self.db.add(suggestion)
        self.db.flush()
        return suggestion

    def create_many(
        self,
        user_id: int,
        session_id: int,
        brain_dump_id: int | None,
        items: list[dict[str, str]],
        parent_suggestion_id: int | None = None,
    ) -> list[Suggestion]:
        return [
            self.create(
                user_id=user_id,
                session_id=session_id,
                brain_dump_id=brain_dump_id,
                title=item["title"],
                micro_step=item["micro_step"],
                effort_level=item["effort_level"],
                parent_suggestion_id=parent_suggestion_id,
                generation_type=item.get(
                    "generation_type",
                    SuggestionGenerationType.original.value,
                ),
                source=item.get("source", SuggestionSource.rule_based.value),
            )
            for item in items
        ]
