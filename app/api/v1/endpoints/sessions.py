from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession

from app.core.db import get_db
from app.schemas.session import SessionCreate, SessionRead
from app.services.session_service import SessionService

router = APIRouter()


@router.post("", response_model=SessionRead, status_code=201)
def create_session(payload: SessionCreate, db: DbSession = Depends(get_db)):
    return SessionService(db).create(context_note=payload.context_note)
