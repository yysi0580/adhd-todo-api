from datetime import timedelta

from fastapi.testclient import TestClient

from app.core.security import create_access_token


def test_register_and_login_success(client: TestClient):
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "auth-success@example.com",
            "password": "password123",
            "nickname": "시열",
        },
    )
    assert register_response.status_code == 201
    assert register_response.json()["email"] == "auth-success@example.com"
    assert register_response.json()["nickname"] == "시열"
    assert "password_hash" not in register_response.text

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "auth-success@example.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]
    assert login_response.json()["refresh_token"]


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
    assert "nickname" in response.json()
    assert "password_hash" not in response.text


def test_users_me_returns_nickname(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"email": "nickname@example.com", "password": "password123", "nickname": "닉네임"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "nickname@example.com", "password": "password123"},
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "닉네임"


def test_register_rejects_blank_nickname(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "blank-nick@example.com", "password": "password123", "nickname": "   "},
    )

    assert response.status_code == 422


def test_existing_user_without_nickname_still_returns_me(
    client: TestClient,
):
    client.post(
        "/api/v1/auth/register",
        json={"email": "no-nickname@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "no-nickname@example.com", "password": "password123"},
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] is None


def test_update_me_changes_nickname(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"nickname": "새닉네임"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "새닉네임"
    assert "password_hash" not in response.text


def test_update_me_rejects_blank_nickname(client: TestClient, auth_headers: dict[str, str]):
    response = client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"nickname": " "},
    )

    assert response.status_code == 422


def test_expired_access_token_is_rejected(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"email": "expired-token@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "expired-token@example.com", "password": "password123"},
    )
    access_token = create_access_token(
        subject=str(
            client.get(
                "/api/v1/users/me",
                headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
            ).json()["id"]
        ),
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401


def test_refresh_token_reissues_access_token(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "refresh@example.com", "password": "password123"},
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_register_rejects_weak_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@example.com", "password": "password"},
    )

    assert response.status_code == 400
    assert response.json()["code"] == "WEAK_PASSWORD"


def test_login_is_blocked_after_repeated_failures(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"email": "blocked@example.com", "password": "password123"},
    )

    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "blocked@example.com", "password": "wrong-password"},
        )
        assert response.status_code == 400

    blocked_response = client.post(
        "/api/v1/auth/login",
        json={"email": "blocked@example.com", "password": "password123"},
    )

    assert blocked_response.status_code == 429
    assert blocked_response.json()["detail"]["code"] == "LOGIN_BLOCKED"
