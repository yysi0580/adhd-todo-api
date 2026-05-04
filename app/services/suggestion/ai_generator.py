import logging

from app.domain.enums import SuggestionGenerationType, SuggestionSource
from app.services.ai.client import OpenAIResponsesClient
from app.services.ai.prompts import build_brain_dump_input, build_make_smaller_input
from app.services.ai.schemas import SuggestionCandidate
from app.services.suggestion.generator import SuggestionGenerator

logger = logging.getLogger(__name__)


class AiSuggestionGenerator:
    def __init__(self, ai_client: OpenAIResponsesClient, fallback: SuggestionGenerator):
        self.ai_client = ai_client
        self.fallback = fallback

    def generate_from_brain_dump(
        self,
        raw_text: str,
        session_context: str | None = None,
    ) -> list[dict[str, str]]:
        try:
            response = self.ai_client.create_suggestions(
                build_brain_dump_input(raw_text=raw_text, session_context=session_context)
            )
            return self._normalize_candidates(
                response.suggestions,
                limit=5,
                generation_type=SuggestionGenerationType.original.value,
            )
        except Exception:
            logger.exception(
                "AI suggestion generation failed; falling back to rule-based generator"
            )
            return self.fallback.generate_micro_steps(raw_text, limit=5)

    def make_smaller(self, title: str, micro_step: str) -> list[dict[str, str]]:
        try:
            response = self.ai_client.create_suggestions(
                build_make_smaller_input(title, micro_step)
            )
            return self._normalize_candidates(
                response.suggestions,
                limit=3,
                generation_type=SuggestionGenerationType.smaller.value,
            )
        except Exception:
            logger.exception(
                "AI make_smaller generation failed; falling back to rule-based generator"
            )
            return self.fallback.generate_smaller_steps(micro_step, limit=3)

    def generate_micro_steps(self, raw_text: str, limit: int = 5) -> list[dict[str, str]]:
        return self.generate_from_brain_dump(raw_text)[:limit]

    def generate_smaller_step(self, text: str) -> dict[str, str]:
        return self.generate_smaller_steps(text, limit=1)[0]

    def generate_smaller_steps(self, text: str, limit: int = 3) -> list[dict[str, str]]:
        return self.make_smaller(title=text, micro_step=text)[:limit]

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
