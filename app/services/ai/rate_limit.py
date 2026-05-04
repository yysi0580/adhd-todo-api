from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.time import utc_now
from app.services.ai.exceptions import AIRateLimitExceededError


@dataclass
class AILimitCounter:
    count: int
    reset_at: datetime


class InMemoryAiRateLimitService:
    """Process-local AI rate limiter. TODO: replace with Redis in production."""

    def __init__(self):
        self._counters: dict[str, AILimitCounter] = {}

    def enforce(self, key: str, limit: int, window_seconds: int) -> None:
        now = utc_now()
        counter = self._counters.get(key)
        if counter is None or counter.reset_at <= now:
            self._counters[key] = AILimitCounter(
                count=1,
                reset_at=now + timedelta(seconds=window_seconds),
            )
            return

        counter.count += 1
        if counter.count > limit:
            raise AIRateLimitExceededError(
                "AI 요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
                code="AI_RATE_LIMIT_EXCEEDED",
            )

    def clear(self) -> None:
        self._counters.clear()


ai_rate_limiter = InMemoryAiRateLimitService()
