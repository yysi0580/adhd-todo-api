from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post("", response_model=FeedbackRead, status_code=201)
def create_feedback(payload: FeedbackCreate, db: DbSession = Depends(get_db)):
    return FeedbackService(db).create(
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        action_id=payload.action_id,
        reaction=payload.reaction,
        note=payload.note,
    )
