from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_brain_dump_creates_session_and_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={
            "raw_text": (
                "프로젝트 발표 준비해야 하는데 자료도 정리해야 하고 "
                "교수님께 질문 메일도 보내야 하고 팀원한테 일정도 공유해야 함"
            )
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session"]["id"] > 0
    assert body["brain_dump"]["user_id"] == body["session"]["user_id"]
    assert 2 <= len(body["suggestions"]) <= 5
    micro_steps = [suggestion["micro_step"] for suggestion in body["suggestions"]]
    assert "발표 자료 제목만 작성하기" in micro_steps
    assert "교수님께 질문 메일 초안 한 줄 쓰기" in micro_steps
    assert "팀원에게 일정 공유 메시지 초안 쓰기" in micro_steps
    assert all(
        suggestion["generation_type"] in {"original", "safety_net"}
        for suggestion in body["suggestions"]
    )


def test_brain_dump_uses_existing_session_when_session_id_is_given(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_response = client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"context_note": "reuse me"},
    )
    session_id = session_response.json()["id"]

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"session_id": session_id, "raw_text": "메일 보내기. 자료 열기"},
    )

    assert response.status_code == 201
    assert response.json()["session"]["id"] == session_id


def test_brain_dump_can_use_active_routine_as_safety_net(
    client: TestClient,
    auth_headers: dict[str, str],
    monkeypatch,
):
    monkeypatch.setattr("app.services.suggestion.generator.SAFETY_NET_ACTIONS", [])
    client.post(
        "/api/v1/routines",
        headers=auth_headers,
        json={"title": "물 한 컵", "micro_step": "컵에 물을 따라 한 모금 마십니다."},
    )

    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "메일"},
    )

    assert response.status_code == 201
    suggestions = response.json()["suggestions"]
    assert any(suggestion["title"] == "물 한 컵" for suggestion in suggestions)
    assert any(suggestion["generation_type"] == "safety_net" for suggestion in suggestions)


def test_brain_dump_rate_limit_applies(client: TestClient, auth_headers: dict[str, str]):
    settings = get_settings()
    original_limit = settings.brain_dump_rate_limit_per_minute
    settings.brain_dump_rate_limit_per_minute = 1
    try:
        first_response = client.post(
            "/api/v1/brain-dumps",
            headers=auth_headers,
            json={"raw_text": "첫 번째 입력"},
        )
        second_response = client.post(
            "/api/v1/brain-dumps",
            headers=auth_headers,
            json={"raw_text": "두 번째 입력"},
        )
    finally:
        settings.brain_dump_rate_limit_per_minute = original_limit

    assert first_response.status_code == 201
    assert second_response.status_code == 429
    assert second_response.json()["detail"]["code"] == "RATE_LIMITED"
