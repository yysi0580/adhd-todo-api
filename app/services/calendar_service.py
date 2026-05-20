from datetime import UTC, datetime

from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError, PermissionDeniedError, ValidationDomainError
from app.domain.time import utc_now
from app.models import CalendarEvent
from app.repositories.calendar_candidate_repository import CalendarCandidateRepository
from app.repositories.calendar_event_repository import CalendarEventRepository
from app.services.common import require_action, require_session


class CalendarService:
    def __init__(self, db: DbSession):
        self.db = db
        self.events = CalendarEventRepository(db)

    def list(
        self,
        user_id: int,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        limit: int = 100,
    ) -> list[CalendarEvent]:
        return self.events.list_for_user(user_id, start_at=start_at, end_at=end_at, limit=limit)

    def create(
        self,
        user_id: int,
        start_at: datetime,
        end_at: datetime,
        title: str | None = None,
        description: str | None = None,
        timezone: str = "Asia/Seoul",
        location: str | None = None,
        session_id: int | None = None,
        action_id: int | None = None,
        candidate_id: int | None = None,
        source: str = "manual",
        display_color: str | None = None,
        is_soft_block: bool = True,
    ) -> CalendarEvent:
        self._validate_range(start_at, end_at)
        if session_id is not None:
            require_session(self.db, user_id=user_id, session_id=session_id)

        if candidate_id is not None:
            candidate = CalendarCandidateRepository(self.db).get(candidate_id)
            if candidate is None:
                raise NotFoundError(
                    "캘린더 후보를 찾을 수 없습니다.",
                    code="CALENDAR_CANDIDATE_NOT_FOUND",
                )
            if candidate.user_id != user_id:
                raise PermissionDeniedError(
                    "캘린더 후보 접근 권한이 없습니다.",
                    code="CALENDAR_CANDIDATE_FORBIDDEN",
                )
            if session_id is not None and candidate.session_id != session_id:
                raise ValidationDomainError(
                    "캘린더 후보가 해당 세션에 속하지 않습니다.",
                    code="CALENDAR_CANDIDATE_SESSION_MISMATCH",
                )
            session_id = session_id or candidate.session_id

        action = None
        if action_id is not None:
            action = require_action(self.db, user_id=user_id, action_id=action_id)
            if session_id is not None and action.session_id != session_id:
                raise ValidationDomainError(
                    "액션이 해당 세션에 속하지 않습니다.",
                    code="ACTION_SESSION_MISMATCH",
                )
            session_id = session_id or action.session_id
            title = title or action.title
            description = description or action.micro_step
            source = source if source != "manual" else "action"

        if not title:
            raise ValidationDomainError(
                "캘린더 이벤트 제목이 필요합니다.",
                code="CALENDAR_EVENT_TITLE_REQUIRED",
            )

        event = self.events.create(
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
            display_color=display_color,
            is_soft_block=is_soft_block,
        )
        event.external_uid = f"adhd-todo-event-{event.id}@yangtheory.site"
        self.db.commit()
        self.db.refresh(event)
        return event

    def read(self, user_id: int, event_id: int) -> CalendarEvent:
        return self._require_event(user_id, event_id)

    def update(
        self,
        user_id: int,
        event_id: int,
        title: str | None = None,
        description: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
        timezone: str | None = None,
        location: str | None = None,
    ) -> CalendarEvent:
        event = self._require_event(user_id, event_id)
        next_start = start_at or event.start_at
        next_end = end_at or event.end_at
        self._validate_range(next_start, next_end)

        if title is not None:
            event.title = title
        if description is not None:
            event.description = description
        if start_at is not None:
            event.start_at = start_at
        if end_at is not None:
            event.end_at = end_at
        if timezone is not None:
            event.timezone = timezone
        if location is not None:
            event.location = location
        event.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(event)
        return event

    def delete(self, user_id: int, event_id: int) -> None:
        event = self._require_event(user_id, event_id)
        self.events.delete(event)
        self.db.commit()

    def export_ics(
        self,
        user_id: int,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> str:
        events = self.list(user_id, start_at=start_at, end_at=end_at, limit=500)
        return build_ics_calendar(events)

    def _require_event(self, user_id: int, event_id: int) -> CalendarEvent:
        event = self.events.get(event_id)
        if event is None:
            raise NotFoundError(
                "캘린더 이벤트를 찾을 수 없습니다.", code="CALENDAR_EVENT_NOT_FOUND"
            )
        if event.user_id != user_id:
            raise PermissionDeniedError(
                "캘린더 이벤트 접근 권한이 없습니다.",
                code="CALENDAR_EVENT_FORBIDDEN",
            )
        return event

    def _validate_range(self, start_at: datetime, end_at: datetime) -> None:
        if end_at <= start_at:
            raise ValidationDomainError(
                "종료 시간은 시작 시간보다 뒤여야 합니다.",
                code="CALENDAR_EVENT_INVALID_RANGE",
            )


def build_ics_calendar(events: list[CalendarEvent]) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ADHD Todo//Calendar//KO",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:ADHD Todo",
    ]
    stamp = _format_ics_datetime(utc_now())
    for event in events:
        uid = event.external_uid or f"adhd-todo-event-{event.id}@yangtheory.site"
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{_escape_ics(uid)}",
                f"DTSTAMP:{stamp}",
                f"DTSTART:{_format_ics_datetime(event.start_at)}",
                f"DTEND:{_format_ics_datetime(event.end_at)}",
                f"SUMMARY:{_escape_ics(event.title)}",
            ]
        )
        if event.description:
            lines.append(f"DESCRIPTION:{_escape_ics(event.description)}")
        if event.location:
            lines.append(f"LOCATION:{_escape_ics(event.location)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold_ics_line(line) for line in lines) + "\r\n"


def _format_ics_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _escape_ics(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\r\n", "\\n")
        .replace("\n", "\\n")
    )


def _fold_ics_line(line: str) -> str:
    encoded = line.encode("utf-8")
    if len(encoded) <= 75:
        return line

    chunks: list[str] = []
    current = ""
    current_size = 0
    for char in line:
        char_size = len(char.encode("utf-8"))
        if current and current_size + char_size > 75:
            chunks.append(current)
            current = f" {char}"
            current_size = 1 + char_size
        else:
            current += char
            current_size += char_size
    chunks.append(current)
    return "\r\n".join(chunks)
