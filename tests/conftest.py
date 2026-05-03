import pytest
from fastapi.testclient import TestClient

from app.core.db import init_db
from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    init_db()
    return TestClient(app)
