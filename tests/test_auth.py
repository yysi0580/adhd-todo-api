from fastapi.testclient import TestClient


def test_register_and_login_success(client: TestClient):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "auth-success@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "auth-success@example.com"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "auth-success@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


def test_login_fails_with_wrong_password(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong-password@example.com", "password": "password123"},
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong-password@example.com", "password": "not-right"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_LOGIN"


def test_protected_api_requires_token(client: TestClient):
    response = client.post("/api/v1/sessions", json={"context_note": "no token"})

    assert response.status_code == 401


def test_users_me_returns_current_user(client: TestClient, auth_headers: dict[str, str]):
    response = client.get("/api/v1/users/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["email"].endswith("@example.com")
