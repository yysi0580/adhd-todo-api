import json
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.services.ai.exceptions import AIInvalidResponseError
from app.services.ai.prompts import (
    build_brain_dump_input,
    build_make_smaller_input,
    current_system_prompt,
)
from app.services.ai.quality import (
    hard_failures,
    validate_candidate_quality,
    validate_make_smaller_quality,
    validate_response_quality,
)
from app.services.ai.schemas import AISuggestionResponse, SuggestionCandidate
from app.services.suggestion.ai_generator import AiSuggestionGenerator
from app.services.suggestion.generator import RuleBasedSuggestionGenerator


def _response(items: list[tuple[str, str]]) -> AISuggestionResponse:
    return AISuggestionResponse(
        suggestions=[
            SuggestionCandidate(title=title, micro_step=micro_step, effort_level="quiet")
            for title, micro_step in items
        ]
    )


def test_quality_rejects_pressure_language():
    response = _response(
        [
            ("무조건 끝내기", "실패하지 않게 반드시 다 끝내기"),
            ("파일 열기", "발표 자료 파일만 열기"),
        ]
    )

    with pytest.raises(AIInvalidResponseError):
        response.validate_for_feature("brain_dump")


def test_quality_rejects_too_large_action():
    issues = validate_candidate_quality("프로젝트", "프로젝트 완성하기")

    assert "error:action_too_big" in issues


def test_quality_rejects_blank_candidate():
    response = _response([("", "파일 열기"), ("메일", "")])

    with pytest.raises(AIInvalidResponseError):
        response.validate_for_feature("brain_dump")


def test_make_smaller_rejects_same_as_original():
    response = _response([("발표 자료 정리하기", "발표 자료 정리하기")])

    issues = validate_make_smaller_quality(
        "발표 자료 정리하기",
        "발표 자료 정리하기",
        response,
    )

    assert hard_failures(issues)


def test_make_smaller_accepts_smaller_start_action():
    response = _response([("파일 열기", "발표 자료 파일만 열기")])

    issues = validate_make_smaller_quality(
        "발표 자료 정리하기",
        "발표 자료 전체 흐름 정리하기",
        response,
    )

    assert not hard_failures(issues)


def test_response_counts_are_feature_specific():
    _response([("파일", "파일 열기"), ("메일", "메일 첫 줄 쓰기")]).validate_for_feature(
        "brain_dump"
    )
    _response([("파일", "파일 열기")]).validate_for_feature("make_smaller")

    with pytest.raises(AIInvalidResponseError):
        _response([("파일", "파일 열기")]).validate_for_feature("brain_dump")
    with pytest.raises(AIInvalidResponseError):
        _response(
            [
                ("하나", "파일 열기"),
                ("둘", "메일 첫 줄 쓰기"),
                ("셋", "제목만 쓰기"),
                ("넷", "물건 하나 치우기"),
            ]
        ).validate_for_feature("make_smaller")


def test_fixture_cases_have_valid_mock_responses():
    cases = json.loads(Path("tests/fixtures/ai_quality_cases.json").read_text(encoding="utf-8"))
    valid_response = _response(
        [
            ("파일 열기", "관련 파일만 열기"),
            ("첫 줄 쓰기", "메모장에 첫 줄만 쓰기"),
            ("3개 고르기", "필요한 항목 3개만 고르기"),
        ]
    )

    for case in cases:
        prompt = build_brain_dump_input(case["raw_text"])
        assert case["raw_text"] in prompt
        assert not hard_failures(validate_response_quality(valid_response, "brain_dump"))


def test_prompt_version_v2_is_in_prompts():
    assert "prompt_version: v2" in current_system_prompt()
    assert "완료할 일" in current_system_prompt()
    assert "prompt_version: v2" in build_brain_dump_input("메일 답장해야 함")
    assert "원본을 같은 말로 반복하지 않는다" in build_make_smaller_input(
        "메일 답장",
        "메일 답장 쓰기",
    )


def test_prompt_version_is_used_in_cache_key(monkeypatch):
    settings = get_settings()
    settings.ai_prompt_version = "v2"

    class StubClient:
        model = "test-model"

    generator = AiSuggestionGenerator(
        ai_client=StubClient(),
        fallback=RuleBasedSuggestionGenerator(),
    )

    v2_key = generator._cache_key("AI_SUGGESTION", 1, "메일 답장")
    settings.ai_prompt_version = "v1"
    v1_key = generator._cache_key("AI_SUGGESTION", 1, "메일 답장")

    assert ":v2:" in v2_key
    assert ":v1:" in v1_key
    assert v1_key != v2_key


def test_general_quality_tests_do_not_require_openai_key():
    settings = get_settings()
    settings.ai_suggestion_enabled = False
    settings.openai_api_key = None

    response = _response([("파일", "파일 열기"), ("메일", "메일 첫 줄 쓰기")])

    assert response.validate_for_feature("brain_dump")
