from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import User
from app.schemas.history import HistoryResponse
from app.services.history_service import HistoryService

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
def read_my_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: DbSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HistoryService(db).read_recent(user_id=current_user.id, limit=limit)
