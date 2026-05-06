from datetime import datetime

from sqlalchemy.orm import Session as DbSession

from app.models import EmailVerificationToken, User


class EmailVerificationRepository:
    def __init__(self, db: DbSession):
        self.db = db

    def create(self, user_id: int, token_hash: str, expires_at: datetime) -> EmailVerificationToken:
        token = EmailVerificationToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.flush()
        return token

    def get_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        return (
            self.db.query(EmailVerificationToken)
            .filter(EmailVerificationToken.token_hash == token_hash)
            .first()
        )

    def latest_unused_for_user(self, user_id: int) -> EmailVerificationToken | None:
        return (
            self.db.query(EmailVerificationToken)
            .filter(
                EmailVerificationToken.user_id == user_id,
                EmailVerificationToken.used_at.is_(None),
            )
            .order_by(EmailVerificationToken.created_at.desc())
            .first()
        )

    def mark_used(self, token: EmailVerificationToken, used_at: datetime) -> EmailVerificationToken:
        token.used_at = used_at
        self.db.flush()
        return token

    def mark_user_verified(self, user: User, verified_at: datetime) -> User:
        user.email_verified = True
        user.email_verified_at = verified_at
        self.db.flush()
        return user
