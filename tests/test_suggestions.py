from conftest import register_and_login
from fastapi.testclient import TestClient


def test_make_smaller_creates_one_to_three_smaller_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "프로젝트 발표 자료 정리하기"},
    )
    original = dump_response.json()["suggestions"][0]

    response = client.post(
        f"/api/v1/suggestions/{original['id']}/make-smaller",
        headers=auth_headers,
    )

    assert response.status_code == 201
    smaller_suggestions = response.json()
    assert 1 <= len(smaller_suggestions) <= 3
    assert all(item["micro_step"] != original["micro_step"] for item in smaller_suggestions)
    assert all(item["parent_suggestion_id"] == original["id"] for item in smaller_suggestions)
    assert all(item["generation_type"] == "smaller" for item in smaller_suggestions)
    assert any(
        "열기" in item["micro_step"] or "제목만" in item["micro_step"]
        for item in smaller_suggestions
    )


def test_short_input_uses_safety_net_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "아"},
    )

    assert response.status_code == 201
    suggestions = response.json()["suggestions"]
    assert len(suggestions) >= 2
    assert any("물" in suggestion["title"] for suggestion in suggestions)
    assert any(suggestion["generation_type"] == "safety_net" for suggestion in suggestions)


def test_other_user_cannot_make_suggestion_smaller(
    client: TestClient,
    auth_headers: dict[str, str],
):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "자료 정리하기"},
    )
    suggestion_id = dump_response.json()["suggestions"][0]["id"]
    other_headers = register_and_login(client)

    response = client.post(
        f"/api/v1/suggestions/{suggestion_id}/make-smaller",
        headers=other_headers,
    )

    assert response.status_code == 403
