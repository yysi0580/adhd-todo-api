import logging
import re

from app.core.config import get_settings
from app.domain.enums import SuggestionGenerationType, SuggestionSource
from app.repositories.ai_usage_log_repository import AiUsageLogRepository
from app.services.ai.budget import AIBudgetGuard
from app.services.ai.cache import ai_cache, hash_ai_input, normalize_ai_input
from app.services.ai.client import OpenAIResponsesClient
from app.services.ai.cost import AIUsage, estimate_cost
from app.services.ai.exceptions import (
    AIBudgetExceededError,
    AIDailyLimitExceededError,
    AIRateLimitExceededError,
)
from app.services.ai.prompts import build_brain_dump_input, build_make_smaller_input
from app.services.ai.quality import hard_failures, validate_make_smaller_quality
from app.services.ai.rate_limit import ai_rate_limiter
from app.services.ai.schemas import AISuggestionResponse, SuggestionCandidate
from app.services.ai.usage_logger import AIUsageLog, ai_usage_logger
from app.services.suggestion.generator import SuggestionGenerator

logger = logging.getLogger(__name__)


class _AIProviderFailureLogged(Exception):
    pass


class AiSuggestionGenerator:
    def __init__(self, ai_client: OpenAIResponsesClient, fallback: SuggestionGenerator, db=None):
        self.ai_client = ai_client
        self.fallback = fallback
        self.db = db
        self.usage_logs = AiUsageLogRepository(db) if db is not None else None
        self.budget_guard = AIBudgetGuard(self.usage_logs) if self.usage_logs is not None else None

    def generate_from_brain_dump(
        self,
        raw_text: str,
        session_context: str | None = None,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        prompt = build_brain_dump_input(raw_text=raw_text, session_context=session_context)
        try:
            response = self._create_with_cache_and_limits(
                user_id=user_id,
                feature_name="brain_dump",
                cache_key=self._cache_key("AI_SUGGESTION", user_id, prompt),
                prompt=prompt,
            )
            validated_response = response.validate_for_feature("brain_dump")
            _validate_brain_dump_relevance(raw_text, validated_response)
            return self._normalize_candidates(
                validated_response.suggestions,
                limit=5,
                generation_type=SuggestionGenerationType.original.value,
            )
        except (AIRateLimitExceededError, AIBudgetExceededError, AIDailyLimitExceededError) as exc:
            logger.info(
                "AI guardrail triggered; falling back to rule-based generator: %s", exc.code
            )
            self._log_failure(user_id, "brain_dump", exc.code, actual_openai_call=False)
            return self.fallback.generate_micro_steps(raw_text, limit=5, user_id=user_id)
        except _AIProviderFailureLogged:
            logger.exception("AI provider call failed; falling back to rule-based generator")
            return self.fallback.generate_micro_steps(raw_text, limit=5, user_id=user_id)
        except Exception:
            logger.exception(
                "AI suggestion generation failed; falling back to rule-based generator"
            )
            self._log_failure(
                user_id, "brain_dump", "AI_INVALID_RESPONSE", actual_openai_call=False
            )
            return self.fallback.generate_micro_steps(raw_text, limit=5, user_id=user_id)

    def make_smaller(
        self,
        title: str,
        micro_step: str,
        user_id: int | None = None,
        suggestion_id: int | None = None,
    ) -> list[dict[str, str]]:
        prompt = build_make_smaller_input(title, micro_step)
        cache_identity = str(suggestion_id) if suggestion_id is not None else prompt
        try:
            response = self._create_with_cache_and_limits(
                user_id=user_id,
                feature_name="make_smaller",
                cache_key=self._cache_key("AI_SMALLER", user_id, cache_identity),
                prompt=prompt,
            )
            validated_response = response.validate_for_feature("make_smaller")
            make_smaller_failures = hard_failures(
                validate_make_smaller_quality(title, micro_step, validated_response)
            )
            if make_smaller_failures:
                raise ValueError("AI make_smaller response failed quality validation")
            return self._normalize_candidates(
                validated_response.suggestions,
                limit=3,
                generation_type=SuggestionGenerationType.smaller.value,
            )
        except (AIRateLimitExceededError, AIBudgetExceededError, AIDailyLimitExceededError) as exc:
            logger.info(
                "AI guardrail triggered; falling back to rule-based generator: %s", exc.code
            )
            self._log_failure(user_id, "make_smaller", exc.code, actual_openai_call=False)
            return self.fallback.generate_smaller_steps(micro_step, limit=3, user_id=user_id)
        except _AIProviderFailureLogged:
            logger.exception("AI provider call failed; falling back to rule-based generator")
            return self.fallback.generate_smaller_steps(micro_step, limit=3, user_id=user_id)
        except Exception:
            logger.exception(
                "AI make_smaller generation failed; falling back to rule-based generator"
            )
            self._log_failure(
                user_id, "make_smaller", "AI_INVALID_RESPONSE", actual_openai_call=False
            )
            return self.fallback.generate_smaller_steps(micro_step, limit=3, user_id=user_id)

    def generate_micro_steps(
        self,
        raw_text: str,
        limit: int = 5,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        return self.generate_from_brain_dump(raw_text, user_id=user_id)[:limit]

    def generate_smaller_step(self, text: str, user_id: int | None = None) -> dict[str, str]:
        return self.generate_smaller_steps(text, limit=1, user_id=user_id)[0]

    def generate_smaller_steps(
        self,
        text: str,
        limit: int = 3,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        return self.make_smaller(title=text, micro_step=text, user_id=user_id)[:limit]

    def _create_with_cache_and_limits(
        self,
        user_id: int | None,
        feature_name: str,
        cache_key: str,
        prompt: str,
    ) -> AISuggestionResponse:
        settings = get_settings()
        if settings.ai_cache_enabled:
            cached = ai_cache.get(cache_key)
            if cached is not None:
                self._log_usage(
                    user_id=user_id,
                    feature_name=feature_name,
                    usage=AIUsage(),
                    cache_hit=True,
                    success=True,
                    actual_openai_call=False,
                )
                return cached

        self._enforce_rate_limit(user_id)
        if self.budget_guard is not None:
            self.budget_guard.enforce(user_id)

        try:
            result = self.ai_client.create_suggestions(prompt)
        except Exception as exc:
            self._log_failure(
                user_id,
                feature_name,
                "AI_SERVICE_ERROR",
                actual_openai_call=True,
            )
            raise _AIProviderFailureLogged from exc
        response = getattr(result, "response", result)
        usage = getattr(result, "usage", AIUsage())

        self._log_usage(
            user_id=user_id,
            feature_name=feature_name,
            usage=usage,
            cache_hit=False,
            success=True,
            actual_openai_call=True,
        )

        if settings.ai_cache_enabled:
            ai_cache.set(cache_key, response, ttl_minutes=settings.ai_cache_ttl_minutes)
        return response

    def _enforce_rate_limit(self, user_id: int | None) -> None:
        settings = get_settings()
        if user_id is None:
            ai_rate_limiter.enforce(
                key="ai:anonymous:unknown:minute",
                limit=settings.ai_rate_limit_anonymous_per_ip_per_minute,
                window_seconds=60,
            )
            return

        ai_rate_limiter.enforce(
            key=f"ai:user:{user_id}:minute",
            limit=settings.ai_rate_limit_per_user_per_minute,
            window_seconds=60,
        )
        ai_rate_limiter.enforce(
            key=f"ai:user:{user_id}:day",
            limit=settings.ai_rate_limit_per_user_per_day,
            window_seconds=86_400,
        )

    def _cache_key(self, prefix: str, user_id: int | None, value: str) -> str:
        settings = get_settings()
        user_key = user_id if user_id is not None else "anonymous"
        return (
            f"{prefix}:{user_key}:{self.ai_client.model}:"
            f"{settings.ai_prompt_version}:{hash_ai_input(normalize_ai_input(value))}"
        )

    def _log_usage(
        self,
        user_id: int | None,
        feature_name: str,
        usage: AIUsage,
        cache_hit: bool,
        success: bool,
        actual_openai_call: bool,
        error_code: str | None = None,
    ) -> None:
        settings = get_settings()
        if not settings.ai_cost_log_enabled:
            return

        estimated_cost = estimate_cost(
            usage,
            input_price_per_1m=settings.ai_cost_input_per_1m,
            cached_input_price_per_1m=settings.ai_cost_cached_input_per_1m,
            output_price_per_1m=settings.ai_cost_output_per_1m,
        )
        ai_usage_logger.log(
            AIUsageLog(
                user_id=user_id,
                feature_name=feature_name,
                model=self.ai_client.model,
                prompt_version=settings.ai_prompt_version,
                input_tokens=usage.input_tokens,
                cached_tokens=usage.cached_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=estimated_cost,
                cache_hit=cache_hit,
                actual_openai_call=actual_openai_call,
                success=success,
                error_code=error_code,
            )
        )
        if self.usage_logs is not None:
            self.usage_logs.create(
                user_id=user_id,
                feature_name=feature_name,
                model=self.ai_client.model,
                prompt_version=settings.ai_prompt_version,
                input_tokens=usage.input_tokens,
                cached_tokens=usage.cached_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
                estimated_cost=estimated_cost,
                cache_hit=cache_hit,
                actual_openai_call=actual_openai_call,
                source=self._usage_source(cache_hit=cache_hit, success=success),
                success=success,
                fallback_used=not success,
                error_code=error_code,
            )

    def _log_failure(
        self,
        user_id: int | None,
        feature_name: str,
        error_code: str,
        actual_openai_call: bool,
    ) -> None:
        self._log_usage(
            user_id=user_id,
            feature_name=feature_name,
            usage=AIUsage(),
            cache_hit=False,
            success=False,
            actual_openai_call=actual_openai_call,
            error_code=error_code,
        )

    def _usage_source(self, cache_hit: bool, success: bool) -> str:
        if cache_hit:
            return "ai_cache"
        if success:
            return SuggestionSource.ai.value
        return "fallback"

    def _normalize_candidates(
        self,
        candidates: list[SuggestionCandidate],
        limit: int,
        generation_type: str,
    ) -> list[dict[str, str]]:
        if not candidates:
            raise ValueError("AI returned empty suggestions")

        normalized = [
            {
                "title": candidate.title.strip(),
                "micro_step": candidate.micro_step.strip(),
                "effort_level": candidate.effort_level,
                "generation_type": generation_type,
                "source": SuggestionSource.ai.value,
            }
            for candidate in candidates
            if candidate.title.strip() and candidate.micro_step.strip()
        ][:limit]

        minimum = 1 if generation_type == SuggestionGenerationType.smaller.value else 2
        if len(normalized) < minimum:
            raise ValueError("AI returned too few valid suggestions")
        return normalized


RELEVANCE_KEYWORDS = (
    "밥",
    "식사",
    "약",
    "복용",
    "알바",
    "출근",
    "근무",
    "이력서",
    "지원서",
    "자소서",
    "메일",
    "교수",
    "팀",
    "일정",
    "발표",
    "자료",
    "병원",
    "예약",
    "운동",
    "청소",
    "방",
    "전화",
    "서류",
)


def _validate_brain_dump_relevance(raw_text: str, response: AISuggestionResponse) -> None:
    keywords = _extract_relevance_keywords(raw_text)
    if not keywords:
        return

    relevant_count = 0
    for suggestion in response.suggestions:
        combined = f"{suggestion.title} {suggestion.micro_step}"
        if any(keyword in combined for keyword in keywords):
            relevant_count += 1

    minimum_relevant = max(1, min(2, len(response.suggestions)))
    if relevant_count < minimum_relevant:
        raise ValueError("AI response did not reflect the brain dump input")


def _extract_relevance_keywords(raw_text: str) -> set[str]:
    keywords = {keyword for keyword in RELEVANCE_KEYWORDS if keyword in raw_text}
    for token in re.findall(r"[가-힣A-Za-z0-9]+", raw_text):
        if len(token) >= 3:
            keywords.add(token[:6])
    return keywords
