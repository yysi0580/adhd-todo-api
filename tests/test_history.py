from conftest import register_and_login
from fastapi.testclient import TestClient


def test_my_history_returns_recent_owned_records(
    client: TestClient,
    auth_headers: dict[str, str],
):
    dump_response = client.post(
        "/api/v1/brain-dumps",
        headers=auth_headers,
        json={"raw_text": "교수님 메일 보내고 팀 일정 공유"},
    )
    dump_body = dump_response.json()
    session_id = dump_body["session"]["id"]
    suggestion_id = dump_body["suggestions"][0]["id"]
    client.post(
        "/api/v1/feedback",
        headers=auth_headers,
        json={"session_id": session_id, "suggestion_id": suggestion_id, "reaction": "do"},
    )

    response = client.get("/api/v1/me/history", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["sessions"]
    assert body["brain_dumps"]
    assert body["actions"]
    assert body["feedback"]


def test_history_does_not_mix_other_user_data(client: TestClient):
    first_headers = register_and_login(client)
    second_headers = register_and_login(client)
    client.post(
        "/api/v1/brain-dumps",
        headers=first_headers,
        json={"raw_text": "첫 번째 사용자 데이터"},
    )

    response = client.get("/api/v1/me/history", headers=second_headers)

    assert response.status_code == 200
    assert response.json()["sessions"] == []
    assert response.json()["brain_dumps"] == []
