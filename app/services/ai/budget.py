from datetime import timedelta

from app.core.config import get_settings
from app.domain.time import utc_now
from app.repositories.ai_usage_log_repository import AiUsageLogRepository
from app.services.ai.exceptions import AIBudgetExceededError, AIDailyLimitExceededError


class AIBudgetGuard:
    def __init__(self, usage_logs: AiUsageLogRepository):
        self.usage_logs = usage_logs

    def enforce(self, user_id: int | None) -> None:
        settings = get_settings()
        now = utc_now()
        day_start = now - timedelta(days=1)
        month_start = now - timedelta(days=30)

        if self.usage_logs.count_since(day_start) >= settings.ai_daily_global_limit:
            raise AIDailyLimitExceededError(
                "AI 일일 호출 제한에 도달했습니다. 기본 제안기로 계속 진행합니다.",
                code="AI_DAILY_LIMIT_EXCEEDED",
            )

        if self.usage_logs.cost_since(day_start) >= settings.ai_daily_global_cost_limit_usd:
            raise AIBudgetExceededError(
                "AI 일일 예산 제한에 도달했습니다. 기본 제안기로 계속 진행합니다.",
                code="AI_BUDGET_EXCEEDED",
            )

        if self.usage_logs.cost_since(month_start) >= settings.ai_monthly_global_cost_limit_usd:
            raise AIBudgetExceededError(
                "AI 월간 예산 제한에 도달했습니다. 기본 제안기로 계속 진행합니다.",
                code="AI_MONTHLY_BUDGET_EXCEEDED",
            )

        if (
            user_id is not None
            and self.usage_logs.cost_since(day_start, user_id=user_id)
            >= settings.ai_per_user_daily_cost_limit_usd
        ):
            raise AIBudgetExceededError(
                "사용자 AI 일일 예산 제한에 도달했습니다. 기본 제안기로 계속 진행합니다.",
                code="AI_BUDGET_EXCEEDED",
            )
