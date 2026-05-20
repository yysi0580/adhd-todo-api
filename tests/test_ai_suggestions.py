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


class IrrelevantAiClient(FakeAiClient):
    def create_suggestions(self, user_input: str) -> AISuggestionResponse:
        type(self).calls += 1
        return AISuggestionResponse(
            suggestions=[
                SuggestionCandidate(
                    title="메모장 열기",
                    micro_step="휴대폰이나 컴퓨터에서 메모장 앱을 연다.",
                    effort_level="quiet",
                ),
                SuggestionCandidate(
                    title="주변 관찰하기",
                    micro_step="주변에 있는 물건이나 소리를 1분간 살펴본다.",
                    effort_level="gentle",
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
    original_global_limit = settings.ai_daily_global_limit
    original_global_cost = settings.ai_daily_global_cost_limit_usd
    original_user_cost = settings.ai_per_user_daily_cost_limit_usd
    original_monthly_cost = settings.ai_monthly_global_cost_limit_usd
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
    settings.ai_daily_global_limit = original_global_limit
    settings.ai_daily_global_cost_limit_usd = original_global_cost
    settings.ai_per_user_daily_cost_limit_usd = original_user_cost
    settings.ai_monthly_global_cost_limit_usd = original_monthly_cost
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


def test_ai_irrelevant_output_falls_back_to_rule_based(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, IrrelevantAiClient)

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "밥먹고 약먹고 알바갔다가 이력서10개 제출"},
    )

    assert response.status_code == 201
    suggestions = response.json()["suggestions"]
    assert all(suggestion["source"] == "rule_based" for suggestion in suggestions)
    micro_steps = [suggestion["micro_step"] for suggestion in suggestions]
    assert "약과 물을 먼저 꺼내기" in micro_steps
    assert "이력서 파일 하나만 열기" in micro_steps


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
    usage_response = client.get("/api/v1/ai/usage/me", headers=auth_headers)
    usage_body = usage_response.json()
    assert usage_body["todayCalls"] == 1
    assert usage_body["cacheHits"] >= 1


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
    assert second_response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in second_response.json()["suggestions"]
    )
    assert FakeAiClient.calls == 1
    usage_body = client.get("/api/v1/ai/usage/me", headers=auth_headers).json()
    assert usage_body["todayCalls"] == 1
    assert usage_body["fallbackReasons"]["AI_RATE_LIMIT_EXCEEDED"] >= 1


def test_ai_budget_guard_falls_back_without_openai_call(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    settings = get_settings()
    settings.ai_cache_enabled = False
    settings.ai_daily_global_limit = 0

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "예산 제한 요청"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )
    assert FakeAiClient.calls == 0
    usage_body = client.get("/api/v1/ai/usage/me", headers=auth_headers).json()
    assert usage_body["todayCalls"] == 0
    assert usage_body["fallbackReasons"]["AI_DAILY_LIMIT_EXCEEDED"] >= 1


def test_ai_daily_cost_guard_falls_back_without_openai_call(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    settings = get_settings()
    settings.ai_cache_enabled = False
    settings.ai_daily_global_cost_limit_usd = 0

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "일일 비용 제한 요청"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )
    assert FakeAiClient.calls == 0
    usage_body = client.get("/api/v1/ai/usage/me", headers=auth_headers).json()
    assert usage_body["todayCalls"] == 0
    assert usage_body["fallbackReasons"]["AI_BUDGET_EXCEEDED"] >= 1


def test_ai_monthly_cost_guard_falls_back_without_openai_call(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    settings = get_settings()
    settings.ai_cache_enabled = False
    settings.ai_daily_global_cost_limit_usd = 999
    settings.ai_per_user_daily_cost_limit_usd = 999
    settings.ai_monthly_global_cost_limit_usd = 0

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "월간 비용 제한 요청"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )
    assert FakeAiClient.calls == 0
    usage_body = client.get("/api/v1/ai/usage/me", headers=auth_headers).json()
    assert usage_body["todayCalls"] == 0
    assert usage_body["fallbackReasons"]["AI_MONTHLY_BUDGET_EXCEEDED"] >= 1


def test_ai_provider_error_counts_as_actual_call_and_fallback_reason(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, ErrorAiClient)
    settings = get_settings()
    settings.ai_cache_enabled = False

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "AI 오류 fallback 요청"},
    )

    assert response.status_code == 201
    assert all(
        suggestion["source"] == "rule_based" for suggestion in response.json()["suggestions"]
    )
    usage_body = client.get("/api/v1/ai/usage/me", headers=auth_headers).json()
    assert usage_body["todayCalls"] == 1
    assert usage_body["fallbackReasons"]["AI_SERVICE_ERROR"] >= 1


def test_ai_status_and_usage_api_returns_safe_state(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    _enable_ai(monkeypatch, FakeAiClient)
    brain_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내고 팀 일정 공유해야 함"},
    )

    status_response = client.get("/api/v1/ai/status", headers=auth_headers)
    usage_response = client.get("/api/v1/ai/usage/me", headers=auth_headers)

    assert brain_response.status_code == 201
    assert status_response.status_code == 200
    status_body = status_response.json()
    assert status_body["enabled"] is True
    assert status_body["model"] == "test-model"
    assert "OPENAI_API_KEY" not in status_response.text

    assert usage_response.status_code == 200
    usage_body = usage_response.json()
    assert usage_body["todayCalls"] >= 1
    assert usage_body["todayEstimatedCost"] >= 0
    assert "fallbackReasons" in usage_body


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
