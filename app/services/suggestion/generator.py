from typing import Protocol

from app.services.suggestion.micro_step_builder import build_micro_step, build_smaller_step
from app.services.suggestion.safety_net import SAFETY_NET_ACTIONS
from app.services.suggestion.splitter import split_brain_dump


class SuggestionGenerator(Protocol):
    def generate_micro_steps(self, raw_text: str, limit: int = 5) -> list[dict[str, str]]:
        """Turn unstructured text into small action candidates."""

    def generate_smaller_step(self, text: str) -> dict[str, str]:
        """Shrink an existing suggestion into a lower-effort first step."""


class RuleBasedSuggestionGenerator:
    """Deterministic MVP implementation.

    This keeps the product honest for now: no AI claims, predictable output,
    and a clean replacement point for a future LLM-backed implementation.
    """

    def generate_micro_steps(self, raw_text: str, limit: int = 5) -> list[dict[str, str]]:
        candidates = [build_micro_step(part) for part in split_brain_dump(raw_text)]

        if not candidates:
            candidates = [
                {
                    "title": title,
                    "micro_step": micro_step,
                    "effort_level": "tiny",
                }
                for title, micro_step in SAFETY_NET_ACTIONS
            ]

        return candidates[:limit]

    def generate_smaller_step(self, text: str) -> dict[str, str]:
        return build_smaller_step(text)


def get_suggestion_generator() -> SuggestionGenerator:
    return RuleBasedSuggestionGenerator()
