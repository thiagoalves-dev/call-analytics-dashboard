from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/calls"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "local-demo-only-secret-replace-in-production"
    jwt_ttl_minutes: int = 8 * 60
    cookie_name: str = "access_token"
    cookie_secure: bool = False

    seed_calls_per_account: int = 500_000
    seed_days: int = 90
    demo_api_key_acme: str = "demo-acme-ingest-key"
    demo_api_key_summit: str = "demo-summit-ingest-key"


@lru_cache
def get_settings() -> Settings:
    return Settings()
