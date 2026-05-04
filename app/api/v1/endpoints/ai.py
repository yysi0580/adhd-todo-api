from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.ai import AIStatusResponse, AIUsageMeResponse
from app.services.ai_status_service import AIStatusService

router = APIRouter()


@router.get("/status", response_model=AIStatusResponse)
def read_ai_status(db: DbSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return AIStatusService(db).status()


@router.get("/usage/me", response_model=AIUsageMeResponse)
def read_my_ai_usage(
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return AIStatusService(db).usage_for_user(current_user.id)
