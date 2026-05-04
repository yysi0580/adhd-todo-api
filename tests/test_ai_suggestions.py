import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.ai.cache import ai_cache
from app.services.ai.cost import AIUsage, estimate_cost
from app.services.ai.rate_limit import ai_rate_limiter
from app.services.ai.schemas import AISuggestionResponse, SuggestionCandidate


class FakeAiClient:
    calls = 0

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model

    def create_suggestions(self, user_input: str) -> AISuggestionResponse:
        type(self).calls += 1
        if "부담스럽게" in user_input:
            return AISuggestionResponse(
                suggestions=[
                    SuggestionCandidate(
                        title="파일만 열기",
                        micro_step="발표 자료 파일만 열기",
                        effort_level="quiet",
                        reason="시작 장벽을 낮춘다",
                    )
                ]
            )
        return AISuggestionResponse(
            suggestions=[
                SuggestionCandidate(
                    title="메일 첫 줄 쓰기",
                    micro_step="교수님께 보낼 메일 첫 줄만 쓰기",
                    effort_level="quiet",
                    reason="시작 문장을 만든다",
                ),
                SuggestionCandidate(
                    title="일정 메시지 초안",
                    micro_step="팀원에게 보낼 일정 공유 메시지 초안 한 줄 쓰기",
                    effort_level="gentle",
                    reason="공유 준비를 작게 만든다",
                ),
            ]
        )


class ErrorAiClient(FakeAiClient):
    def create_suggestions(self, user_input: str) -> AISuggestionResponse:
        raise RuntimeError("AI unavailable")


class EmptyAiClient(FakeAiClient):
    def create_suggestions(self, user_input: str) -> AISuggestionResponse:
        return AISuggestionResponse(suggestions=[])


class PressureAiClient(FakeAiClient):
    def create_suggestions(self, user_input: str) -> AISuggestionResponse:
        return AISuggestionResponse(
            suggestions=[
                SuggestionCandidate(
                    title="반드시 해야 하는 일",
                    micro_step="실패하지 않게 반드시 해야 한다",
                    effort_level="neutral",
                ),
                SuggestionCandidate(
                    title="다른 일",
                    micro_step="다른 일을 시작하기",
                    effort_level="quiet",
                ),
            ]
        )


@pytest.fixture(autouse=True)
def restore_ai_settings():
    settings = get_settings()
    original_enabled = settings.ai_suggestion_enabled
    original_key = settings.openai_api_key
    original_model = settings.ai_model
    original_minute = settings.ai_rate_limit_per_user_per_minute
    original_day = settings.ai_rate_limit_per_user_per_day
    original_cache = settings.ai_cache_enabled
    original_cost_log = settings.ai_cost_log_enabled
    ai_cache.clear()
    ai_rate_limiter.clear()
    FakeAiClient.calls = 0
    yield
    settings.ai_suggestion_enabled = original_enabled
    settings.openai_api_key = original_key
    settings.ai_model = original_model
    settings.ai_rate_limit_per_user_per_minute = original_minute
    settings.ai_rate_limit_per_user_per_day = original_day
    settings.ai_cache_enabled = original_cache
    settings.ai_cost_log_enabled = original_cost_log
    ai_cache.clear()
    ai_rate_limiter.clear()


def test_ai_enabled_saves_ai_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내고 팀 일정 공유해야 함"},
    )

    assert response.status_code == 201
    suggestions = response.json()["suggestions"]
    assert len(suggestions) == 2
    assert all(suggestion["source"] == "ai" for suggestion in suggestions)
    assert suggestions[0]["effort_level"] == "quiet"


def test_ai_disabled_uses_rule_based_generator(
    client: TestClient,
    auth_headers: dict[str, str],
):
    settings = get_settings()
    original_enabled = settings.ai_suggestion_enabled
    original_key = settings.openai_api_key
    settings.ai_suggestion_enabled = False
    settings.openai_api_key = "test-key"
    try:
        response = client.post(
            "/api/v1/brain-dumps",
            headers=auth_headers,
            json={"raw_text": "교수님 메일 보내야 함"},
        )
    finally:
        settings.ai_suggestion_enabled = original_enabled
        settings.openai_api_key = original_key

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )


def test_ai_enabled_without_api_key_uses_rule_based_generator(
    client: TestClient,
    auth_headers: dict[str, str],
):
    settings = get_settings()
    settings.ai_suggestion_enabled = True
    settings.openai_api_key = None

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내야 함"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )


def test_ai_error_falls_back_to_rule_based(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, ErrorAiClient)

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내야 함"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )


def test_ai_make_smaller_creates_ai_smaller_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "발표 자료 정리하기"},
    )
    original = dump_response.json()["suggestions"][0]

    response = client.post(
        f"/api/v1/suggestions/{original['id']}/make-smaller",
        headers=auth_headers,
    )

    assert response.status_code == 201
    smaller = response.json()
    assert len(smaller) == 1
    assert smaller[0]["source"] == "ai"
    assert smaller[0]["generation_type"] == "smaller"
    assert smaller[0]["parent_suggestion_id"] == original["id"]


def test_ai_make_smaller_error_falls_back_to_rule_based(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, ErrorAiClient)
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "발표 자료 정리하기"},
    )
    original = dump_response.json()["suggestions"][0]

    response = client.post(
        f"/api/v1/suggestions/{original['id']}/make-smaller",
        headers=auth_headers,
    )

    assert response.status_code == 201
    smaller = response.json()
    assert 1 <= len(smaller) <= 3
    assert all(suggestion["source"] == "rule_based" for suggestion in smaller)
    assert all(suggestion["generation_type"] == "smaller" for suggestion in smaller)


def test_ai_invalid_output_falls_back_to_rule_based(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, EmptyAiClient)

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내야 함"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )


def test_ai_pressure_language_falls_back_to_rule_based(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, PressureAiClient)

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내야 함"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )


def test_ai_cache_reuses_same_request(
    client: TestClient, auth_headers: dict[str, str], monkeypatch
):
    _enable_ai(monkeypatch, FakeAiClient)

    for _ in range(2):
        response = client.post(
            "/api/v1/brain-dumps",
            headers=auth_headers,
            json={"raw_text": "교수님 메일 보내고 팀 일정 공유해야 함"},
        )
        assert response.status_code == 201

    assert FakeAiClient.calls == 1


def test_ai_rate_limit_blocks_openai_call(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    settings = get_settings()
    settings.ai_cache_enabled = False
    settings.ai_rate_limit_per_user_per_minute = 1

    first_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "첫 번째 요청"},
    )
    second_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "두 번째 요청"},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["code"] == "AI_RATE_LIMIT_EXCEEDED"
    assert FakeAiClient.calls == 1


def test_ai_cost_calculation_uses_cached_token_price():
    cost = estimate_cost(
        AIUsage(input_tokens=1000, cached_tokens=250, output_tokens=500, total_tokens=1500),
        input_price_per_1m=0.40,
        cached_input_price_per_1m=0.10,
        output_price_per_1m=1.60,
    )

    assert cost == pytest.approx(0.001125)


def test_openai_api_key_is_not_hardcoded():
    source_files = [
        "app/core/config.py",
        "app/services/ai/client.py",
        ".env.example",
    ]
    for path in source_files:
        assert "sk-" not in open(path, encoding="utf-8").read()


def _enable_ai(monkeypatch, fake_client: type[FakeAiClient]) -> None:
    settings = get_settings()
    settings.ai_suggestion_enabled = True
    settings.openai_api_key = "test-key"
    settings.ai_model = "test-model"
    monkeypatch.setattr("app.services.ai.client.OpenAIResponsesClient", fake_client)
