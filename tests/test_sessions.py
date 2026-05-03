from fastapi.testclient import TestClient


def test_create_session(client: TestClient):
    response = client.post("/api/v1/sessions", json={"context_note": "late night planning"})

    assert response.status_code == 201
    assert response.json()["context_note"] == "late night planning"
