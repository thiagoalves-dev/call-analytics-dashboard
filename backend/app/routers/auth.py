from fastapi import APIRouter, Response, status

from app.actions.auth.login import Login
from app.actions.auth.show_current_user import ShowCurrentUser
from app.config import get_settings
from app.dependencies.auth import CurrentPrincipal
from app.dependencies.database import Session
from app.schemas.auth import LoginRequest, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECONDS_PER_MINUTE = 60


@router.post("/login")
async def login(body: LoginRequest, response: Response, session: Session) -> UserResponse:
    result = await Login(session, body.email, body.password)()
    set_session_cookie(response, result.access_token)
    return result.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response) -> None:
    response.delete_cookie(get_settings().cookie_name, path="/")


@router.get("/me")
async def me(principal: CurrentPrincipal, session: Session) -> UserResponse:
    return await ShowCurrentUser(session, principal.user_id)()


def set_session_cookie(response: Response, access_token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        settings.cookie_name,
        access_token,
        max_age=settings.jwt_ttl_minutes * SECONDS_PER_MINUTE,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
