from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.calendar_candidate import (
    CalendarCandidateFromSuggestions,
    CalendarCandidateRead,
    CalendarCandidateSchedule,
    CalendarCandidateScheduleFromSuggestion,
    CalendarCandidateScheduleResponse,
)
from app.services.calendar_candidate_service import CalendarCandidateService

router = APIRouter()


@router.get("", response_model=list[CalendarCandidateRead])
def list_calendar_candidates(
    session_id: int,
    limit: int = 100,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarCandidateService(db).list_for_session(
        current_user.id,
        session_id=session_id,
        limit=min(limit, 200),
    )


@router.post("/from-suggestions", response_model=list[CalendarCandidateRead], status_code=201)
def create_calendar_candidates_from_suggestions(
    payload: CalendarCandidateFromSuggestions,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CalendarCandidateService(db).create_from_suggestions(
        current_user.id,
        session_id=payload.session_id,
        suggestion_ids=payload.suggestion_ids,
    )


@router.post("/from-suggestion/schedule", response_model=CalendarCandidateScheduleResponse)
def schedule_calendar_candidate_from_suggestion(
    payload: CalendarCandidateScheduleFromSuggestion,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate, event = CalendarCandidateService(db).schedule_from_suggestion(
        current_user.id,
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        timezone=payload.timezone,
        location=payload.location,
        placement_source=payload.placement_source,
        is_locked=payload.is_locked,
        user_note=payload.user_note,
    )
    return {"candidate": candidate, "event": event}


@router.post("/{candidate_id}/schedule", response_model=CalendarCandidateScheduleResponse)
def schedule_calendar_candidate(
    candidate_id: int,
    payload: CalendarCandidateSchedule,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate, event = CalendarCandidateService(db).schedule(
        current_user.id,
        candidate_id=candidate_id,
        start_at=payload.start_at,
        end_at=payload.end_at,
        timezone=payload.timezone,
        location=payload.location,
        placement_source=payload.placement_source,
        is_locked=payload.is_locked,
        user_note=payload.user_note,
    )
    return {"candidate": candidate, "event": event}
