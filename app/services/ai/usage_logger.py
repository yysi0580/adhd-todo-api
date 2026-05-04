import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AIUsageLog:
    user_id: int | None
    feature_name: str
    model: str
    prompt_version: str
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    cache_hit: bool = False
    actual_openai_call: bool = False
    success: bool = True
    error_code: str | None = None


class AIUsageLogger:
    """Writes operational AI usage details to application logs."""

    def log(self, entry: AIUsageLog) -> None:
        logger.info(
            "ai_usage user_id=%s feature=%s model=%s prompt_version=%s "
            "input_tokens=%s cached_tokens=%s output_tokens=%s total_tokens=%s "
            "estimated_cost=%.8f cache_hit=%s actual_openai_call=%s success=%s error_code=%s",
            entry.user_id,
            entry.feature_name,
            entry.model,
            entry.prompt_version,
            entry.input_tokens,
            entry.cached_tokens,
            entry.output_tokens,
            entry.total_tokens,
            entry.estimated_cost,
            entry.cache_hit,
            entry.actual_openai_call,
            entry.success,
            entry.error_code,
        )


ai_usage_logger = AIUsageLogger()
