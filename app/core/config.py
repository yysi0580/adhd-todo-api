from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ADHD Todo API"
    database_url: str = "sqlite:///./adhd_todo.db"
    environment: str = "local"
    auto_create_tables: bool = True
    jwt_secret_key: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    login_failure_limit: int = 5
    login_block_minutes: int = 5
    login_rate_limit_per_minute: int = 20
    brain_dump_rate_limit_per_minute: int = 60
    openai_api_key: str | None = None
    ai_suggestion_enabled: bool = False
    ai_model: str = "gpt-4.1-mini"
    cors_origins: list[str] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://yangtheory.site:5173",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
