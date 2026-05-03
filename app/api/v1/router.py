from fastapi import APIRouter

from app.api.v1.endpoints import actions, brain_dumps, feedback, health, sessions, suggestions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(brain_dumps.router, prefix="/brain-dumps", tags=["brain-dumps"])
api_router.include_router(suggestions.router, tags=["suggestions"])
api_router.include_router(actions.router, prefix="/actions", tags=["actions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
