from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.services.feedback_service import FeedbackService
from app.services.suggestion import SuggestionGenerator, get_suggestion_generator

router = APIRouter()


@router.post("", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    payload: FeedbackCreate,
    db: DbSession = Depends(get_db),
    generator: SuggestionGenerator = Depends(get_suggestion_generator),
    current_user: User = Depends(get_current_user),
):
    feedback, smaller_suggestions = FeedbackService(db, generator).create(
        user_id=current_user.id,
        session_id=payload.session_id,
        suggestion_id=payload.suggestion_id,
        action_id=payload.action_id,
        reaction=payload.reaction.value,
        note=payload.note,
    )
    return {
        "feedback": feedback,
        "action_id": feedback.action_id,
        "smaller_suggestions": smaller_suggestions,
    }
