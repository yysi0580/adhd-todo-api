from fastapi.testclient import TestClient

from app.core.db import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_brain_dump_creates_session_and_suggestions():
    response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "발표 준비해야 하고 교수님 메일 보내야 함, 팀 일정 공유"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session"]["id"] > 0
    assert body["brain_dump"]["raw_text"]
    assert len(body["suggestions"]) >= 2


def test_select_suggestion_as_action():
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "문서 만들고 제목 정해야 함"},
    )
    dump_body = dump_response.json()
    session_id = dump_body["session"]["id"]
    suggestion_id = dump_body["suggestions"][0]["id"]

    action_response = client.post(
        "/api/v1/actions",
        json={"session_id": session_id, "suggestion_id": suggestion_id},
    )

    assert action_response.status_code == 201
    assert action_response.json()["status"] == "active"


def test_complete_action_endpoint_sets_status():
    dump_response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "교수님 메일 보내야 함"},
    )
    dump_body = dump_response.json()
    action_response = client.post(
        "/api/v1/actions",
        json={
            "session_id": dump_body["session"]["id"],
            "suggestion_id": dump_body["suggestions"][0]["id"],
        },
    )
    action_id = action_response.json()["id"]

    complete_response = client.post(f"/api/v1/actions/{action_id}/complete")

    assert complete_response.status_code == 200
    assert complete_response.json()["status"] == "completed"


def test_feedback_requires_existing_related_target():
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
