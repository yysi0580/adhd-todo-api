import os

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_REAL_AI_SMOKE") != "true",
    reason="Set RUN_REAL_AI_SMOKE=true to run real OpenAI smoke tests.",
)


def test_real_ai_brain_dump_and_make_smaller(
    client: TestClient,
    auth_headers: dict[str, str],
):
    settings = get_settings()
    if not settings.openai_api_key or not settings.ai_suggestion_enabled:
        pytest.skip("OPENAI_API_KEY and AI_SUGGESTION_ENABLED=true are required.")

    brain_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={
            "raw_text": "프로젝트 발표 준비해야 하는데 자료 정리하고 교수님께 질문 메일도 보내야 함"
        },
    )

    assert brain_response.status_code == 201
    suggestions = brain_response.json()["suggestions"]
    assert 2 <= len(suggestions) <= 5
    assert all(suggestion["source"] == "ai" for suggestion in suggestions)

    target = suggestions[0]
    smaller_response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={
            "session_id": target["session_id"],
            "suggestion_id": target["id"],
            "reaction": "make_smaller",
        },
    )

    assert smaller_response.status_code == 201
    smaller = smaller_response.json()["smaller_suggestions"]
    assert 1 <= len(smaller) <= 3
    assert all(item["source"] == "ai" for item in smaller)
