from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.suggestion import SuggestionRead
from app.services.suggestion import SuggestionGenerator, get_suggestion_generator
from app.services.suggestion_service import SuggestionService

router = APIRouter()


@router.get("/sessions/{session_id}/suggestions", response_model=list[SuggestionRead])
def list_suggestions(session_id: int, db: DbSession = Depends(get_db)):
    return SuggestionService(db, get_suggestion_generator()).list_by_session(session_id)


@router.post(
    "/suggestions/{suggestion_id}/make-smaller",
    response_model=SuggestionRead,
    status_code=201,
)
def make_suggestion_smaller(
    suggestion_id: int,
    db: DbSession = Depends(get_db),
    generator: SuggestionGenerator = Depends(get_suggestion_generator),
):
    return SuggestionService(db, generator).make_smaller(suggestion_id)
