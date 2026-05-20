from datetime import datetime

from sqlalchemy.orm import Session as DbSession

from app.models import CalendarEvent


class CalendarEventRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def get(self, event_id: int) -> CalendarEvent | None:
        return self.db.get(CalendarEvent, event_id)

    def list_for_user(
        self,
        user_id: int,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int = 100,
    ) -> list[CalendarEvent]:
        query = self.db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
        if start_at:
            query = query.filter(CalendarEvent.end_at >= start_at)
        if end_at:
            query = query.filter(CalendarEvent.start_at <= end_at)
        return query.order_by(CalendarEvent.start_at.asc()).limit(limit).all()

    def create(
        self,
        user_id: int,
        title: str,
        start_at: datetime,
        end_at: datetime,
        description: str | None = None,
        timezone: str = "Asia/Seoul",
        location: str | None = None,
        session_id: int | None = None,
        action_id: int | None = None,
        candidate_id: int | None = None,
        source: str = "manual",
        status: str = "scheduled",
        display_color: str | None = None,
        is_soft_block: bool = True,
    ) -> CalendarEvent:
        event = CalendarEvent(
            user_id=user_id,
            session_id=session_id,
            action_id=action_id,
            candidate_id=candidate_id,
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            timezone=timezone,
            location=location,
            source=source,
            status=status,
            display_color=display_color,
            is_soft_block=is_soft_block,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def delete(self, event: CalendarEvent) -> None:
        self.db.delete(event)
