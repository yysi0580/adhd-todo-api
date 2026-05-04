import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.ai.schemas import SuggestionCandidate, SuggestionResponse


class FakeAiClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def create_suggestions(self, user_input: str) -> SuggestionResponse:
        if "부담스럽게" in user_input:
            return SuggestionResponse(
                suggestions=[
                    SuggestionCandidate(
                        title="파일만 열기",
                        micro_step="발표 자료 파일만 열기",
                        effort_level="quiet",
                        reason="시작 장벽을 낮춘다",
                    )
                ]
            )
        return SuggestionResponse(
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
    def create_suggestions(self, user_input: str) -> SuggestionResponse:
        raise RuntimeError("AI unavailable")


class EmptyAiClient(FakeAiClient):
    def create_suggestions(self, user_input: str) -> SuggestionResponse:
        return SuggestionResponse(suggestions=[])


@pytest.fixture(autouse=True)
def restore_ai_settings():
    settings = get_settings()
    original_enabled = settings.ai_suggestion_enabled
    original_key = settings.openai_api_key
    original_model = settings.ai_model
    yield
    settings.ai_suggestion_enabled = original_enabled
    settings.openai_api_key = original_key
    settings.ai_model = original_model


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


def _enable_ai(monkeypatch, fake_client: type[FakeAiClient]) -> None:
    settings = get_settings()
    settings.ai_suggestion_enabled = True
    settings.openai_api_key = "test-key"
    settings.ai_model = "test-model"
    monkeypatch.setattr("app.services.ai.client.OpenAIResponsesClient", fake_client)
