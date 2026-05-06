from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import get_settings
from app.core.db import Base, get_db
from app.core.limits import reset_limits
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_test_schema() -> Generator:
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client() -> TestClient:
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    return register_and_login(client)


@pytest.fixture(autouse=True)
def clear_in_memory_limits() -> Generator:
    settings = get_settings()
    original_ai_enabled = settings.ai_suggestion_enabled
    original_openai_key = settings.openai_api_key
    original_prompt_version = settings.ai_prompt_version
    settings.ai_suggestion_enabled = False
    settings.openai_api_key = None
    settings.ai_prompt_version = "v2"
    reset_limits()
    yield
    settings.ai_suggestion_enabled = original_ai_enabled
    settings.openai_api_key = original_openai_key
    settings.ai_prompt_version = original_prompt_version
    reset_limits()


def register_and_login(client: TestClient, email: str | None = None) -> dict[str, str]:
    email = email or f"user-{uuid4().hex}@example.com"
    password = "password123"
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
