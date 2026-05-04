from typing import Protocol

from app.core.config import get_settings
from app.domain.enums import SuggestionGenerationType, SuggestionSource
from app.services.suggestion.micro_step_builder import build_micro_step
from app.services.suggestion.safety_net import SAFETY_NET_ACTIONS
from app.services.suggestion.smaller import build_smaller_step, build_smaller_steps
from app.services.suggestion.splitter import split_brain_dump


class SuggestionGenerator(Protocol):
    def generate_micro_steps(
        self,
        raw_text: str,
        limit: int = 5,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        """Turn unstructured text into small action candidates."""

    def generate_smaller_step(
        self,
        text: str,
        user_id: int | None = None,
    ) -> dict[str, str]:
        """Shrink an existing suggestion into a lower-effort first step."""

    def generate_smaller_steps(
        self,
        text: str,
        limit: int = 3,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        """Shrink an existing suggestion into one to three lower-effort steps."""


class RuleBasedSuggestionGenerator:
    """Deterministic MVP implementation.

    This keeps the product honest for now: no AI claims, predictable output,
    and a clean replacement point for a future LLM-backed implementation.
    """

    def generate_micro_steps(
        self,
        raw_text: str,
        limit: int = 5,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        candidates = [build_micro_step(part) for part in split_brain_dump(raw_text)]

        candidates = _ensure_minimum_suggestions(candidates)

        return candidates[:limit]

    def generate_smaller_step(self, text: str, user_id: int | None = None) -> dict[str, str]:
        return build_smaller_step(text)

    def generate_smaller_steps(
        self,
        text: str,
        limit: int = 3,
        user_id: int | None = None,
    ) -> list[dict[str, str]]:
        return build_smaller_steps(text, limit=limit)


def _ensure_minimum_suggestions(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    if not candidates:
        return [
            {
                "title": title,
                "micro_step": micro_step,
                "effort_level": "tiny",
                "generation_type": SuggestionGenerationType.safety_net.value,
                "source": SuggestionSource.rule_based.value,
            }
            for title, micro_step in SAFETY_NET_ACTIONS
        ]

    if len(candidates) == 1:
        candidates[0]["generation_type"] = SuggestionGenerationType.original.value
        used_titles = {candidates[0]["title"]}
        for title, micro_step in SAFETY_NET_ACTIONS:
            if title not in used_titles:
                candidates.append(
                    {
                        "title": title,
                        "micro_step": micro_step,
                        "effort_level": "tiny",
                        "generation_type": SuggestionGenerationType.safety_net.value,
                        "source": SuggestionSource.rule_based.value,
                    }
                )
                break
    else:
        for candidate in candidates:
            candidate["generation_type"] = SuggestionGenerationType.original.value
    for candidate in candidates:
        candidate.setdefault("source", SuggestionSource.rule_based.value)
    return candidates


def get_suggestion_generator() -> SuggestionGenerator:
    settings = get_settings()
    if settings.ai_suggestion_enabled and settings.openai_api_key:
        from app.services.ai.client import OpenAIResponsesClient
        from app.services.suggestion.ai_generator import AiSuggestionGenerator

        return AiSuggestionGenerator(
            ai_client=OpenAIResponsesClient(
                api_key=settings.openai_api_key,
                model=settings.ai_model,
                timeout=settings.ai_timeout_seconds,
                max_output_tokens=settings.ai_max_output_tokens,
            ),
            fallback=RuleBasedSuggestionGenerator(),
        )
    return RuleBasedSuggestionGenerator()
