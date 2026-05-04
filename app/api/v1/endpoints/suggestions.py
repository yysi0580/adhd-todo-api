from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.suggestion import SuggestionRead
from app.services.suggestion import (
    RuleBasedSuggestionGenerator,
    SuggestionGenerator,
    get_suggestion_generator,
)
from app.services.suggestion_service import SuggestionService

router = APIRouter()


@router.get("/sessions/{session_id}/suggestions", response_model=list[SuggestionRead])
def list_suggestions(
    session_id: int,
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SuggestionService(db, RuleBasedSuggestionGenerator()).list_by_session(
        user_id=current_user.id,
        session_id=session_id,
    )


@router.post(
    "/suggestions/{suggestion_id}/make-smaller",
    response_model=list[SuggestionRead],
    status_code=201,
)
def make_suggestion_smaller(
    suggestion_id: int,
    db: DbSession = Depends(get_db),
    generator: SuggestionGenerator = Depends(get_suggestion_generator),
    current_user: User = Depends(get_current_user),
):
    return SuggestionService(db, generator).make_smaller(
        user_id=current_user.id,
        suggestion_id=suggestion_id,
    )
