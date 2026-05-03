import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("reaction", ["do", "snooze", "pass", "make_smaller", "capture_only"])
def test_feedback_reactions_are_saved(client: TestClient, reaction: str):
    dump_response = client.post("/api/v1/brain-dumps", json={"raw_text": "자료 정리하기"})
    dump_body = dump_response.json()
    suggestion_id = dump_body["suggestions"][0]["id"]
    session_id = dump_body["session"]["id"]

    response = client.post(
        "/api/v1/feedback",
        json={"session_id": session_id, "suggestion_id": suggestion_id, "reaction": reaction},
    )

    assert response.status_code == 201
    assert response.json()["reaction"] == reaction


def test_feedback_requires_existing_suggestion(client: TestClient):
    session_response = client.post("/api/v1/sessions", json={"context_note": "test"})
    session_id = session_response.json()["id"]

    missing_suggestion_response = client.post(
        "/api/v1/feedback",
        json={"session_id": session_id, "suggestion_id": 999999, "reaction": "pass"},
    )

    assert missing_suggestion_response.status_code == 404


def test_feedback_rejects_invalid_reaction(client: TestClient):
    dump_response = client.post("/api/v1/brain-dumps", json={"raw_text": "자료 정리하기"})
    dump_body = dump_response.json()

    response = client.post(
        "/api/v1/feedback",
        json={
            "session_id": dump_body["session"]["id"],
            "suggestion_id": dump_body["suggestions"][0]["id"],
            "reaction": "failed",
        },
    )

    assert response.status_code == 422
