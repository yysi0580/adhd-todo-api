import json
from pathlib import Path

import pytest

from app.services.ai.exceptions import AIInvalidResponseError
from app.services.ai.prompts import build_brain_dump_input
from app.services.ai.schemas import AISuggestionResponse, SuggestionCandidate

PRESSURE_WORDS = ("실패", "게으름", "무조건", "반드시", "당장 끝내")


def test_ai_quality_fixture_prompts_are_stable():
    cases = json.loads(Path("tests/fixtures/ai_quality_cases.json").read_text(encoding="utf-8"))

    assert len(cases) >= 10
    for case in cases:
        prompt = build_brain_dump_input(case["raw_text"])
        assert "prompt_version: v2" in prompt
        assert "생성 개수: 2~5" in prompt
        assert case["raw_text"] in prompt
        assert case["expected_quality_notes"]


def test_ai_response_quality_validator_rejects_pressure_language():
    response = AISuggestionResponse(
        suggestions=[
            SuggestionCandidate(
                title="무조건 끝내기",
                micro_step="반드시 다 끝내기",
                effort_level="neutral",
            ),
            SuggestionCandidate(
                title="파일 열기",
                micro_step="파일만 열기",
                effort_level="quiet",
            ),
        ]
    )

    with pytest.raises(AIInvalidResponseError):
        response.validate_for_feature("brain_dump")


def test_ai_response_quality_accepts_small_candidates():
    response = AISuggestionResponse(
        suggestions=[
            SuggestionCandidate(
                title="파일 열기",
                micro_step="발표 자료 파일만 열기",
                effort_level="quiet",
            ),
            SuggestionCandidate(
                title="메일 첫 줄",
                micro_step="교수님께 보낼 메일 첫 줄만 쓰기",
                effort_level="gentle",
            ),
        ]
    )

    validated = response.validate_for_feature("brain_dump")

    assert 2 <= len(validated.suggestions) <= 5
    for suggestion in validated.suggestions:
        assert suggestion.title.strip()
        assert suggestion.micro_step.strip()
        assert suggestion.effort_level in {"quiet", "gentle", "neutral"}
        assert len(suggestion.micro_step) <= 80
        assert not any(word in suggestion.micro_step for word in PRESSURE_WORDS)
