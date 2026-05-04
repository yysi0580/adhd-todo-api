from conftest import register_and_login
from fastapi.testclient import TestClient


def test_create_and_read_session(client: TestClient, auth_headers: dict[str, str]):
    response = client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"context_note": "late night planning"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["context_note"] == "late night planning"
    assert body["user_id"] is not None

    read_response = client.get(f"/api/v1/sessions/{body['id']}", headers=auth_headers)
    assert read_response.status_code == 200
    assert read_response.json()["id"] == body["id"]


def test_other_user_cannot_read_session(client: TestClient, auth_headers: dict[str, str]):
    session_response = client.post(
        "/api/v1/sessions",
        headers=auth_headers,
        json={"context_note": "private"},
    )
    other_headers = register_and_login(client)

    response = client.get(
        f"/api/v1/sessions/{session_response.json()['id']}",
        headers=other_headers,
    )

    assert response.status_code == 404
