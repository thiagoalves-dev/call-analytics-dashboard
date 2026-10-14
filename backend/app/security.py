import hashlib
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.config import get_settings

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int, account_id: int) -> str:
    settings = get_settings()
    issued_at = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "account_id": account_id,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.jwt_ttl_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=[JWT_ALGORITHM])


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
