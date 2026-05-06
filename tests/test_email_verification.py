from datetime import timedelta

from conftest import TestingSessionLocal, register_and_login
from fastapi.testclient import TestClient

from app.domain.time import utc_now
from app.models import EmailVerificationToken, User
from app.services.email_service import EmailService


def test_register_creates_unverified_user_and_hashed_token(
    client: TestClient,
    monkeypatch,
):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "verify-register@example.com",
            "password": "password123",
            "nickname": "인증",
        },
    )

    assert response.status_code == 201
    assert response.json()["email_verified"] is False
    assert captured

    db = TestingSessionLocal()
    try:
        token = (
            db.query(EmailVerificationToken)
            .join(User)
            .filter(User.email == "verify-register@example.com")
            .one()
        )
        assert token.token_hash != captured[0]
        assert len(token.token_hash) == 64
        assert captured[0] not in token.token_hash
    finally:
        db.close()


def test_verify_valid_token_marks_user_verified(client: TestClient, monkeypatch):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "verify-ok@example.com", "password": "password123"},
    )
    assert register_response.status_code == 201

    response = client.post("/api/v1/auth/verify-email", json={"token": captured[0]})

    assert response.status_code == 200
    assert response.json()["message"] == "이메일 인증이 완료되었습니다."

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "verify-ok@example.com", "password": "password123"},
    )
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email_verified"] is True


def test_verify_expired_token_is_rejected(client: TestClient, monkeypatch):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)
    client.post(
        "/api/v1/auth/register",
        json={"email": "verify-expired@example.com", "password": "password123"},
    )

    db = TestingSessionLocal()
    try:
        token = (
            db.query(EmailVerificationToken)
            .join(User)
            .filter(User.email == "verify-expired@example.com")
            .one()
        )
        token.expires_at = utc_now() - timedelta(minutes=1)
        db.commit()
    finally:
        db.close()

    response = client.post("/api/v1/auth/verify-email", json={"token": captured[0]})

    assert response.status_code == 400
    assert response.json()["code"] == "EMAIL_VERIFICATION_TOKEN_EXPIRED"


def test_used_token_is_rejected(client: TestClient, monkeypatch):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)
    client.post(
        "/api/v1/auth/register",
        json={"email": "verify-used@example.com", "password": "password123"},
    )
    first_response = client.post("/api/v1/auth/verify-email", json={"token": captured[0]})
    second_response = client.post("/api/v1/auth/verify-email", json={"token": captured[0]})

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["code"] == "EMAIL_VERIFICATION_TOKEN_USED"


def test_resend_creates_new_token_for_unverified_user(client: TestClient, monkeypatch):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)
    headers = register_and_login(client, email="verify-resend@example.com")

    response = client.post("/api/v1/auth/resend-verification", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "인증 메일을 다시 보냈습니다."
    assert len(captured) == 2


def test_resend_for_verified_user_returns_safe_message(client: TestClient, monkeypatch):
    captured: list[str] = []

    def fake_send(self, user: User, raw_token: str) -> None:
        captured.append(raw_token)

    monkeypatch.setattr(EmailService, "send_verification_email", fake_send)
    headers = register_and_login(client, email="verify-resend-done@example.com")
    verify_response = client.post("/api/v1/auth/verify-email", json={"token": captured[0]})
    assert verify_response.status_code == 200

    response = client.post("/api/v1/auth/resend-verification", headers=headers)

    assert response.status_code == 200
    assert response.json()["message"] == "이미 이메일 인증이 완료되었습니다."
    assert len(captured) == 1
