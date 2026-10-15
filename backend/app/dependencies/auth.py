from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from app.config import get_settings
from app.db import SessionLocal
from app.dependencies.database import Session
from app.models import Account
from app.repositories import account_repository, user_repository
from app.security import decode_access_token


@dataclass(frozen=True)
class Principal:
    user_id: int
    account_id: int


async def current_principal(request: Request) -> Principal:
    principal = principal_from_cookie(request)
    async with SessionLocal() as session:
        user_exists = await user_repository.exists_in_account(session, principal.user_id, principal.account_id)
    if not user_exists:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session")
    return principal


def principal_from_cookie(request: Request) -> Principal:
    token = request.cookies.get(get_settings().cookie_name)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        claims = decode_access_token(token)
    except jwt.InvalidTokenError as error:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired session") from error
    return Principal(user_id=int(claims["sub"]), account_id=int(claims["account_id"]))


async def ingest_account(session: Session, x_api_key: Annotated[str | None, Header()] = None) -> Account:
    if not x_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing X-API-Key header")
    account = await account_repository.find_by_active_api_key(session, x_api_key)
    if account is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")
    return account


CurrentPrincipal = Annotated[Principal, Depends(current_principal)]
IngestAccount = Annotated[Account, Depends(ingest_account)]
