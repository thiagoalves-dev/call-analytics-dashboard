from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, read from environment variables (see docker-compose.yml)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/calls"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "local-demo-only-secret-replace-in-production"
    jwt_ttl_minutes: int = 8 * 60
    cookie_name: str = "access_token"
    # True behind HTTPS. Local docker-compose serves plain HTTP, so the default is False.
    cookie_secure: bool = False

    # Seed size per company. 500k by default; 5M and 50M are documented options.
    seed_calls_per_account: int = 500_000
    seed_days: int = 90
    # Fixed demo API keys so the simulator can authenticate without a setup step.
    demo_api_key_acme: str = "demo-acme-ingest-key"
    demo_api_key_summit: str = "demo-summit-ingest-key"


@lru_cache
def get_settings() -> Settings:
    return Settings()
