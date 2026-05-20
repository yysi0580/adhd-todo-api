from sqlalchemy.orm import Session as DbSession

from app.models import CalendarCandidate


class CalendarCandidateRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, candidate_id: int) -> CalendarCandidate | None:
        return self.db.get(CalendarCandidate, candidate_id)

    def get_by_suggestion(self, user_id: int, suggestion_id: int) -> CalendarCandidate | None:
        return (
            self.db.query(CalendarCandidate)
            .filter(
                CalendarCandidate.user_id == user_id,
                CalendarCandidate.suggestion_id == suggestion_id,
            )
            .order_by(CalendarCandidate.created_at.desc())
            .first()
        )

    def list_for_session(
        self,
        user_id: int,
        session_id: int,
        limit: int = 100,
    ) -> list[CalendarCandidate]:
        return (
            self.db.query(CalendarCandidate)
            .filter(
                CalendarCandidate.user_id == user_id,
                CalendarCandidate.session_id == session_id,
            )
            .order_by(CalendarCandidate.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(
        self,
        user_id: int,
        session_id: int,
        title: str,
        micro_step: str,
        candidate_type: str,
        estimated_minutes: int,
        min_minutes: int,
        max_minutes: int,
        preferred_time_block: str,
        energy_level: str,
        friction_level: str,
        split_strategy: str,
        reason: str | None = None,
        suggestion_id: int | None = None,
        action_id: int | None = None,
        calendar_event_id: int | None = None,
        status: str = "proposed",
        timezone: str = "Asia/Seoul",
        placement_source: str = "ai_suggested",
        is_locked: bool = False,
        conflict_status: str = "clear",
        user_note: str | None = None,
    ) -> CalendarCandidate:
        candidate = CalendarCandidate(
            user_id=user_id,
            session_id=session_id,
            suggestion_id=suggestion_id,
            action_id=action_id,
            calendar_event_id=calendar_event_id,
            title=title,
            micro_step=micro_step,
            candidate_type=candidate_type,
            estimated_minutes=estimated_minutes,
            min_minutes=min_minutes,
            max_minutes=max_minutes,
            preferred_time_block=preferred_time_block,
            energy_level=energy_level,
            friction_level=friction_level,
            split_strategy=split_strategy,
            reason=reason,
            status=status,
            timezone=timezone,
            placement_source=placement_source,
            is_locked=is_locked,
            conflict_status=conflict_status,
            user_note=user_note,
        )
        self.db.add(candidate)
        self.db.flush()
        return candidate
