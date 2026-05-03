from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.brain_dump import BrainDumpCreate, BrainDumpResponse
from app.services.brain_dump_service import BrainDumpService
from app.services.suggestion import SuggestionGenerator, get_suggestion_generator

router = APIRouter()


@router.post("", response_model=BrainDumpResponse, status_code=201)
def create_brain_dump(
    payload: BrainDumpCreate,
    db: DbSession = Depends(get_db),
    generator: SuggestionGenerator = Depends(get_suggestion_generator),
) -> dict:
    session, brain_dump, suggestions = BrainDumpService(db, generator).create_with_suggestions(
        raw_text=payload.raw_text,
        session_id=payload.session_id,
    )
    return {"session": session, "brain_dump": brain_dump, "suggestions": suggestions}
