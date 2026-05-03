from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.models.domain import (
    Action,
    ActionStatus,
    BrainDump,
    Feedback,
    Session,
    Suggestion,
    utc_now,
)
from app.schemas.domain import (
    ActionCreate,
    ActionRead,
    ActionUpdate,
    BrainDumpCreate,
    BrainDumpResponse,
    FeedbackCreate,
    FeedbackRead,
    SessionCreate,
    SessionRead,
    SuggestionRead,
)
from app.services.suggestions import SuggestionService, get_suggestion_service

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sessions", response_model=SessionRead, status_code=201)
def create_session(payload: SessionCreate, db: DbSession = Depends(get_db)) -> Session:
    session = Session(context_note=payload.context_note)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/brain-dumps", response_model=BrainDumpResponse, status_code=201)
def create_brain_dump(
    payload: BrainDumpCreate,
    db: DbSession = Depends(get_db),
    suggestion_service: SuggestionService = Depends(get_suggestion_service),
) -> dict:
    session = db.get(Session, payload.session_id) if payload.session_id else Session()
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    db.add(session)
    db.flush()

    brain_dump = BrainDump(session_id=session.id, raw_text=payload.raw_text)
    db.add(brain_dump)
    db.flush()

    suggestions = [
        Suggestion(
            session_id=session.id,
            brain_dump_id=brain_dump.id,
            title=item["title"],
            micro_step=item["micro_step"],
            effort_level=item["effort_level"],
        )
        for item in suggestion_service.generate_micro_steps(payload.raw_text)
    ]
    db.add_all(suggestions)
    db.commit()

    db.refresh(session)
    db.refresh(brain_dump)
    for suggestion in suggestions:
        db.refresh(suggestion)

    return {"session": session, "brain_dump": brain_dump, "suggestions": suggestions}


@router.get("/sessions/{session_id}/suggestions", response_model=list[SuggestionRead])
def list_suggestions(session_id: int, db: DbSession = Depends(get_db)) -> list[Suggestion]:
    _require_session(db, session_id)
    return (
        db.query(Suggestion)
        .filter(Suggestion.session_id == session_id)
        .order_by(Suggestion.created_at.desc())
        .all()
    )


@router.post(
    "/suggestions/{suggestion_id}/make-smaller", response_model=SuggestionRead, status_code=201
)
def make_suggestion_smaller(
    suggestion_id: int,
    db: DbSession = Depends(get_db),
    suggestion_service: SuggestionService = Depends(get_suggestion_service),
) -> Suggestion:
    suggestion = db.get(Suggestion, suggestion_id)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    smaller = suggestion_service.generate_smaller_step(suggestion.micro_step)
    new_suggestion = Suggestion(
        session_id=suggestion.session_id,
        brain_dump_id=suggestion.brain_dump_id,
        title=smaller["title"],
        micro_step=smaller["micro_step"],
        effort_level=smaller["effort_level"],
    )
    db.add(new_suggestion)
    db.commit()
    db.refresh(new_suggestion)
    return new_suggestion


@router.post("/actions", response_model=ActionRead, status_code=201)
def create_action(payload: ActionCreate, db: DbSession = Depends(get_db)) -> Action:
    _require_session(db, payload.session_id)
    suggestion = db.get(Suggestion, payload.suggestion_id) if payload.suggestion_id else None
    if payload.suggestion_id and suggestion is None:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    if suggestion and suggestion.session_id != payload.session_id:
        raise HTTPException(status_code=400, detail="Suggestion does not belong to this session")

    title = payload.title or (suggestion.title if suggestion else None)
    micro_step = payload.micro_step or (suggestion.micro_step if suggestion else None)
    if not title or not micro_step:
        raise HTTPException(
            status_code=400,
            detail="title and micro_step are required without suggestion_id",
        )

    action = Action(
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        title=title,
        micro_step=micro_step,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@router.patch("/actions/{action_id}", response_model=ActionRead)
def update_action(action_id: int, payload: ActionUpdate, db: DbSession = Depends(get_db)) -> Action:
    return _set_action_status(db, action_id, payload.status.value)


@router.post("/actions/{action_id}/complete", response_model=ActionRead)
def complete_action(action_id: int, db: DbSession = Depends(get_db)) -> Action:
    return _set_action_status(db, action_id, ActionStatus.completed.value)


@router.post("/actions/{action_id}/abort", response_model=ActionRead)
def abort_action(action_id: int, db: DbSession = Depends(get_db)) -> Action:
    return _set_action_status(db, action_id, ActionStatus.aborted.value)


def _set_action_status(db: DbSession, action_id: int, status: str) -> Action:
    action = db.get(Action, action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="Action not found")

    action.status = status
    action.updated_at = utc_now()
    db.commit()
    db.refresh(action)
    return action


@router.post("/feedback", response_model=FeedbackRead, status_code=201)
def create_feedback(payload: FeedbackCreate, db: DbSession = Depends(get_db)) -> Feedback:
    _require_session(db, payload.session_id)
    if payload.suggestion_id is None and payload.action_id is None:
        raise HTTPException(
            status_code=400,
            detail="Either suggestion_id or action_id is required",
        )

    if payload.suggestion_id is not None:
        suggestion = db.get(Suggestion, payload.suggestion_id)
        if suggestion is None:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        if suggestion.session_id != payload.session_id:
            raise HTTPException(
                status_code=400,
                detail="Suggestion does not belong to this session",
            )

    if payload.action_id is not None:
        action = db.get(Action, payload.action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Action not found")
        if action.session_id != payload.session_id:
            raise HTTPException(
                status_code=400,
                detail="Action does not belong to this session",
            )

    feedback = Feedback(
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        action_id=payload.action_id,
        reaction=payload.reaction,
        note=payload.note,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def _require_session(db: DbSession, session_id: int) -> Session:
    session = db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
