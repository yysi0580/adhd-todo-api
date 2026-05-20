from datetime import datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventRead,
    CalendarEventUpdate,
)
from app.services.calendar_service import CalendarService

router = APIRouter()


@router.get("/events", response_model=list[CalendarEventRead])
def list_calendar_events(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    limit: int = 100,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarService(db).list(
        current_user.id,
        start_at=start_at,
        end_at=end_at,
        limit=min(limit, 500),
    )


@router.get("/events.ics")
def export_calendar_events_ics(
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    calendar_text = CalendarService(db).export_ics(
        current_user.id,
        start_at=start_at,
        end_at=end_at,
    )
    return Response(
        content=calendar_text,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="adhd-todo-calendar.ics"'},
    )


@router.get("/events/{event_id}", response_model=CalendarEventRead)
def read_calendar_event(
    event_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarService(db).read(current_user.id, event_id)


@router.post("/events", response_model=CalendarEventRead, status_code=201)
def create_calendar_event(
    payload: CalendarEventCreate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarService(db).create(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        start_at=payload.start_at,
        end_at=payload.end_at,
        timezone=payload.timezone,
        location=payload.location,
        session_id=payload.session_id,
        action_id=payload.action_id,
        candidate_id=payload.candidate_id,
        source=payload.source,
    )


@router.patch("/events/{event_id}", response_model=CalendarEventRead)
def update_calendar_event(
    event_id: int,
    payload: CalendarEventUpdate,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarService(db).update(
        user_id=current_user.id,
        event_id=event_id,
        title=payload.title,
        description=payload.description,
        start_at=payload.start_at,
        end_at=payload.end_at,
        timezone=payload.timezone,
        location=payload.location,
    )


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calendar_event(
    event_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CalendarService(db).delete(current_user.id, event_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
