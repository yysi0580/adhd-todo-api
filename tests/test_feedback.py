import pytest
from conftest import register_and_login
from fastapi.testclient import TestClient


def _create_suggestion(client: TestClient, headers: dict[str, str]) -> tuple[int, int]:
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=headers,
        json={"raw_text": "자료 정리하기"},
    )
    dump_body = dump_response.json()
    return dump_body["session"]["id"], dump_body["suggestions"][0]["id"]


@pytest.mark.parametrize("reaction", ["snooze", "pass", "capture_only"])
def test_feedback_reactions_are_saved(
    client: TestClient,
    auth_headers: dict[str, str],
    reaction: str,
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)

    response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id, "reaction": reaction},
    )

    assert response.status_code == 201
    assert response.json()["feedback"]["reaction"] == reaction
    assert response.json()["action_id"] is None


def test_feedback_do_creates_action_and_links_action_id(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)

    response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id, "reaction": "do"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["feedback"]["reaction"] == "do"
    assert body["feedback"]["action_id"] == body["action_id"]
    assert body["action_id"] is not None


def test_feedback_make_smaller_creates_smaller_suggestions(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)

    response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "suggestion_id": suggestion_id,
            "reaction": "make_smaller",
        },
    )

    assert response.status_code == 201
    smaller_suggestions = response.json()["smaller_suggestions"]
    assert 1 <= len(smaller_suggestions) <= 3
    assert all(item["parent_suggestion_id"] == suggestion_id for item in smaller_suggestions)
    assert all(item["generation_type"] == "smaller" for item in smaller_suggestions)


def test_feedback_requires_existing_suggestion(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_response = client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"context_note": "test"},
    )
    session_id = session_response.json()["id"]

    missing_suggestion_response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": 999999, "reaction": "pass"},
    )

    assert missing_suggestion_response.status_code == 404


def test_feedback_rejects_invalid_reaction(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)

    response = client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "suggestion_id": suggestion_id,
            "reaction": "failed",
        },
    )

    assert response.status_code == 422


def test_other_user_cannot_feedback_on_suggestion(
    client: TestClient,
    auth_headers: dict[str, str],
):
    session_id, suggestion_id = _create_suggestion(client, auth_headers)
    other_headers = register_and_login(client)

    response = client.post(
        "/api/v1/feedback",
        headers=other_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id, "reaction": "pass"},
    )

    assert response.status_code == 403
