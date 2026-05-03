from sqlalchemy.orm import Session as DbSession

from app.models import Suggestion


class SuggestionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, suggestion_id: int) -> Suggestion | None:
        return self.db.get(Suggestion, suggestion_id)

    def list_by_session(self, session_id: int) -> list[Suggestion]:
        return (
            self.db.query(Suggestion)
            .filter(Suggestion.session_id == session_id)
            .order_by(Suggestion.created_at.desc())
            .all()
        )

    def create(
        self,
        session_id: int,
        brain_dump_id: int | None,
        title: str,
        micro_step: str,
        effort_level: str,
    ) -> Suggestion:
        suggestion = Suggestion(
            session_id=session_id,
            brain_dump_id=brain_dump_id,
            title=title,
            micro_step=micro_step,
            effort_level=effort_level,
        )
        self.db.add(suggestion)
        self.db.flush()
        return suggestion

    def create_many(
        self,
        session_id: int,
        brain_dump_id: int | None,
        items: list[dict[str, str]],
    ) -> list[Suggestion]:
        return [
            self.create(
                session_id=session_id,
                brain_dump_id=brain_dump_id,
                title=item["title"],
                micro_step=item["micro_step"],
                effort_level=item["effort_level"],
            )
            for item in items
        ]
