import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings
from app.core.exceptions import ValidationDomainError
from app.models import User

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.settings = get_settings()

    def send_email(self, to: str, subject: str, body: str) -> None:
        if not self._smtp_configured():
            if self.settings.environment.lower() == "production":
                raise ValidationDomainError(
                    "SMTP 설정이 필요합니다.",
                    code="SMTP_CONFIG_MISSING",
                )
            logger.info(
                "Email delivery skipped in development. to=%s subject=%s\n%s", to, subject, body
            )
            return

        message = EmailMessage()
        message["From"] = self.settings.mail_from or self.settings.smtp_username
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)

    def send_verification_email(self, user: User, raw_token: str) -> None:
        verification_url = f"{self.settings.frontend_base_url}/verify-email?token={raw_token}"
        body = "\n".join(
            [
                "ADHD Todo 이메일 인증 링크입니다.",
                "",
                "아래 링크를 열어 이메일 인증을 완료해주세요.",
                verification_url,
                "",
                "이 링크는 제한된 시간 동안만 사용할 수 있습니다.",
            ]
        )
        self.send_email(
            to=user.email,
            subject="[ADHD Todo] 이메일 인증을 완료해주세요",
            body=body,
        )

    def _smtp_configured(self) -> bool:
        return bool(
            self.settings.mail_from
            and self.settings.smtp_host
            and self.settings.smtp_username
            and self.settings.smtp_password
        )
