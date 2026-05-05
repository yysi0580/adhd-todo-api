from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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
    ai_timeout_seconds: float = 30
    ai_max_output_tokens: int = 700
    ai_prompt_version: str = "v1"
    ai_rate_limit_per_user_per_minute: int = 10
    ai_rate_limit_per_user_per_day: int = 100
    ai_rate_limit_anonymous_per_ip_per_minute: int = 5
    ai_daily_global_limit: int = 1000
    ai_daily_global_cost_limit_usd: float = 5.0
    ai_per_user_daily_cost_limit_usd: float = 1.0
    ai_monthly_global_cost_limit_usd: float = 50.0
    ai_cache_enabled: bool = True
    ai_cache_ttl_minutes: int = 30
    ai_cost_log_enabled: bool = True
    # OpenAI prices can change. Confirm current pricing before production deploy.
    ai_cost_input_per_1m: float = 0.40
    ai_cost_cached_input_per_1m: float = 0.10
    ai_cost_output_per_1m: float = 1.60
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://yangtheory.site:5173",
        "https://yangtheory.site",
        "http://yangtheory.site",
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8-sig")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_production_settings(settings: Settings) -> None:
    if settings.environment.lower() != "production":
        return
    if settings.jwt_secret_key == "change-this-secret-in-production":
        raise RuntimeError("JWT_SECRET_KEY must be changed in production.")
    if "*" in settings.cors_origins:
        raise RuntimeError("CORS_ORIGINS must not include '*' in production.")
