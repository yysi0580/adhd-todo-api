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
