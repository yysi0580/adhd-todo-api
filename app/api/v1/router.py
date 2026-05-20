from fastapi import APIRouter

from app.api.v1.endpoints import (
    actions,
    ai,
    auth,
    brain_dumps,
    calendar,
    calendar_candidates,
    feedback,
    health,
    history,
    routines,
    sessions,
    suggestions,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(history.router, prefix="/me", tags=["history"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(brain_dumps.router, prefix="/brain-dumps", tags=["brain-dumps"])
api_router.include_router(suggestions.router, tags=["suggestions"])
api_router.include_router(actions.router, prefix="/actions", tags=["actions"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(routines.router, prefix="/routines", tags=["routines"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(
    calendar_candidates.router,
    prefix="/calendar/candidates",
    tags=["calendar-candidates"],
)
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
