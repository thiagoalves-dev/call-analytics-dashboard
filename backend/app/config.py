from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCAL_ENVIRONMENT = "local"
DEMO_JWT_SECRET = "local-demo-only-secret-replace-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = LOCAL_ENVIRONMENT

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/calls"
    redis_url: str = "redis://localhost:6379/0"
    live_channel_prefix: str = "calls:"

    jwt_secret: str = DEMO_JWT_SECRET
    jwt_ttl_minutes: int = 8 * 60
    cookie_name: str = "access_token"
    cookie_secure: bool = False

    seed_calls_per_account: int = 500_000
    seed_days: int = 90
    demo_api_key_acme: str = "demo-acme-ingest-key"
    demo_api_key_summit: str = "demo-summit-ingest-key"

    @model_validator(mode="after")
    def refuse_the_demo_secret_outside_local(self) -> "Settings":
        if self.environment != LOCAL_ENVIRONMENT and self.jwt_secret == DEMO_JWT_SECRET:
            raise ValueError(f"JWT_SECRET must be set when ENVIRONMENT is {self.environment!r}, not the demo default")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
