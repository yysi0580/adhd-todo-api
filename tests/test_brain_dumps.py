from fastapi.testclient import TestClient


def test_brain_dump_creates_session_and_suggestions(client: TestClient):
    response = client.post(
        "/api/v1/brain-dumps",
        json={"raw_text": "발표 준비해야 하고 교수님 메일 보내야 함, 팀 일정 공유"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["session"]["id"] > 0
    assert body["brain_dump"]["raw_text"]
    assert len(body["suggestions"]) >= 2
