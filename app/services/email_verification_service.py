import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.core.exceptions import ValidationDomainError
from app.domain.time import utc_now
from app.models import User
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class EmailVerificationService:
    def __init__(self, db: DbSession, email_service: EmailService | None = None):
        self.db = db
        self.settings = get_settings()
        self.tokens = EmailVerificationRepository(db)
        self.users = UserRepository(db)
        self.email_service = email_service or EmailService()

    def create_token(self, user_id: int) -> str:
        raw_token = secrets.token_urlsafe(32)
        expires_at = utc_now() + timedelta(minutes=self.settings.email_verification_expire_minutes)
        self.tokens.create(
            user_id=user_id,
            token_hash=self._hash_token(raw_token),
            expires_at=expires_at,
        )
        self.db.flush()
        return raw_token

    def send_verification(self, user: User) -> bool:
        raw_token = self.create_token(user.id)
        try:
            self.email_service.send_verification_email(user, raw_token)
        except Exception:
            logger.exception("Email verification delivery failed for user_id=%s", user.id)
            return False
        return True

    def verify_token(self, raw_token: str) -> User:
        token = self.tokens.get_by_hash(self._hash_token(raw_token))
        now = utc_now()
        if token is None:
            raise ValidationDomainError(
                "이메일 인증 링크가 올바르지 않습니다.",
                code="INVALID_EMAIL_VERIFICATION_TOKEN",
            )
        if token.used_at is not None:
            raise ValidationDomainError(
                "이미 사용된 이메일 인증 링크입니다.",
                code="EMAIL_VERIFICATION_TOKEN_USED",
            )
        if self._as_aware(token.expires_at) < now:
            raise ValidationDomainError(
                "이메일 인증 링크가 만료되었습니다.",
                code="EMAIL_VERIFICATION_TOKEN_EXPIRED",
            )

        user = self.users.get(token.user_id)
        if user is None:
            raise ValidationDomainError(
                "이메일 인증 사용자를 찾을 수 없습니다.",
                code="EMAIL_VERIFICATION_USER_NOT_FOUND",
            )

        self.tokens.mark_used(token, now)
        self.tokens.mark_user_verified(user, now)
        self.db.commit()
        self.db.refresh(user)
        return user

    def resend_verification(self, user: User) -> tuple[bool, str]:
        if user.email_verified:
            return True, "이미 이메일 인증이 완료되었습니다."

        sent = self.send_verification(user)
        self.db.commit()
        if sent:
            return True, "인증 메일을 다시 보냈습니다."
        return False, "인증 메일 발송 설정을 확인해야 합니다. 앱은 계속 사용할 수 있습니다."

    def _hash_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    def _as_aware(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
