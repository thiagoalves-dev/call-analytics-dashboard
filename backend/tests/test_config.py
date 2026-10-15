import pytest
from pydantic import ValidationError

from app.config import DEMO_JWT_SECRET, Settings

REAL_SECRET = "a-real-secret-from-the-environment"


def test_refuses_the_demo_jwt_secret_outside_local():
    with pytest.raises(ValidationError, match="JWT_SECRET must be set"):
        Settings(environment="production", jwt_secret=DEMO_JWT_SECRET)


def test_refuses_a_missing_jwt_secret_read_from_the_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError, match="JWT_SECRET must be set"):
        Settings()


def test_accepts_a_real_jwt_secret_outside_local():
    assert Settings(environment="production", jwt_secret=REAL_SECRET).jwt_secret == REAL_SECRET


def test_allows_the_demo_jwt_secret_locally():
    assert Settings(jwt_secret=DEMO_JWT_SECRET).environment == "local"
