import pytest

from app.core.config import Settings, validate_production_settings


def test_production_rejects_default_jwt_secret():
    settings = Settings(environment="production", cors_origins=["https://yangtheory.site"])

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        validate_production_settings(settings)


def test_production_rejects_wildcard_cors():
    settings = Settings(
        environment="production",
        jwt_secret_key="production-secret-value",
        cors_origins=["*"],
    )

    with pytest.raises(RuntimeError, match="CORS_ORIGINS"):
        validate_production_settings(settings)


def test_local_allows_default_development_settings():
    settings = Settings(environment="local", cors_origins=["*"])

    validate_production_settings(settings)
