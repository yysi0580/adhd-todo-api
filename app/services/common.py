from sqlalchemy.orm import Session as DbSession

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models import Action, Session, Suggestion
from app.repositories.action_repository import ActionRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.suggestion_repository import SuggestionRepository


def require_session(db: DbSession, user_id: int, session_id: int) -> Session:
    session = SessionRepository(db).get(session_id)
    if session is None:
        raise NotFoundError("세션을 찾을 수 없습니다.", code="SESSION_NOT_FOUND")
    if session.user_id != user_id:
        raise PermissionDeniedError("세션 접근 권한이 없습니다.", code="SESSION_FORBIDDEN")
    return session


def require_suggestion(db: DbSession, user_id: int, suggestion_id: int) -> Suggestion:
    suggestion = SuggestionRepository(db).get(suggestion_id)
    if suggestion is None:
        raise NotFoundError("제안을 찾을 수 없습니다.", code="SUGGESTION_NOT_FOUND")
    if suggestion.user_id != user_id:
        raise PermissionDeniedError("제안 접근 권한이 없습니다.", code="SUGGESTION_FORBIDDEN")
    return suggestion


def require_action(db: DbSession, user_id: int, action_id: int) -> Action:
    action = ActionRepository(db).get(action_id)
    if action is None:
        raise NotFoundError("액션을 찾을 수 없습니다.", code="ACTION_NOT_FOUND")
    if action.user_id != user_id:
        raise PermissionDeniedError("액션 접근 권한이 없습니다.", code="ACTION_FORBIDDEN")
    return action
