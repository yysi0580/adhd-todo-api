from datetime import timedelta

from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.domain.time import utc_now
from app.repositories.ai_usage_log_repository import AiUsageLogRepository


class AIStatusService:
    def __init__(self, db: DbSession):
        self.db = db
        self.usage_logs = AiUsageLogRepository(db)

    def status(self) -> dict:
        settings = get_settings()
        return {
            "enabled": settings.ai_suggestion_enabled and bool(settings.openai_api_key),
            "model": settings.ai_model,
            "structuredOutput": True,
            "cacheEnabled": settings.ai_cache_enabled,
            "rateLimitEnabled": True,
            "budgetLimitEnabled": True,
            "fallback": "rule_based",
            "promptVersion": settings.ai_prompt_version,
        }

    def usage_for_user(self, user_id: int) -> dict:
        now = utc_now()
        today = now - timedelta(days=1)
        month = now - timedelta(days=30)
        return {
            "todayCalls": self.usage_logs.user_actual_openai_calls_since(today, user_id=user_id),
            "todayEstimatedCost": self.usage_logs.cost_since(today, user_id=user_id),
            "monthlyEstimatedCost": self.usage_logs.cost_since(month, user_id=user_id),
            "cacheHits": self.usage_logs.cache_hits_since(today, user_id=user_id),
            "fallbackCount": self.usage_logs.fallback_count_since(today, user_id=user_id),
            "fallbackReasons": self.usage_logs.fallback_reasons_since(today, user_id=user_id),
            "lastUsedAt": self.usage_logs.last_used_at(user_id),
        }
