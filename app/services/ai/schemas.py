from typing import Literal

from pydantic import BaseModel, Field

from app.services.ai.exceptions import AIInvalidResponseError

PRESSURE_WORDS = ("반드시 해야", "반드시", "무조건", "실패했다", "게으르", "실패", "성취율")


class SuggestionCandidate(BaseModel):
    title: str = Field(description="짧은 행동 후보 제목")
    micro_step: str = Field(description="2~5분 안에 시작 가능한 실제 행동 문장")
    effort_level: Literal["quiet", "gentle", "neutral"]
    reason: str | None = None


class AISuggestionResponse(BaseModel):
    suggestions: list[SuggestionCandidate]

    def validate_for_feature(self, feature_name: str) -> "AISuggestionResponse":
        minimum = 1 if feature_name == "make_smaller" else 2
        maximum = 3 if feature_name == "make_smaller" else 5
        if not minimum <= len(self.suggestions) <= maximum:
            raise AIInvalidResponseError(
                "AI 응답의 suggestion 개수가 유효하지 않습니다.",
                code="AI_INVALID_RESPONSE",
            )

        for suggestion in self.suggestions:
            title = suggestion.title.strip()
            micro_step = suggestion.micro_step.strip()
            if not title or not micro_step:
                raise AIInvalidResponseError(
                    "AI 응답에 빈 suggestion이 포함되어 있습니다.",
                    code="AI_INVALID_RESPONSE",
                )
            if _contains_pressure_language(title) or _contains_pressure_language(micro_step):
                raise AIInvalidResponseError(
                    "AI 응답에 압박 표현이 포함되어 있습니다.",
                    code="AI_INVALID_RESPONSE",
                )
        return self


def _contains_pressure_language(value: str) -> bool:
    normalized = value.replace(" ", "")
    return any(word.replace(" ", "") in normalized for word in PRESSURE_WORDS)


SuggestionResponse = AISuggestionResponse
