from fastapi.testclient import TestClient


def test_feedback_requires_existing_related_target(client: TestClient):
    session_response = client.post("/api/v1/sessions", json={"context_note": "test"})
    session_id = session_response.json()["id"]

    no_target_response = client.post(
        "/api/v1/feedback",
        json={"session_id": session_id, "reaction": "pass"},
    )
    missing_suggestion_response = client.post(
        "/api/v1/feedback",
        json={"session_id": session_id, "suggestion_id": 999999, "reaction": "pass"},
    )

    assert no_target_response.status_code == 400
    assert missing_suggestion_response.status_code == 404
