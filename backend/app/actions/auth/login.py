from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthenticationError
from app.models import User
from app.repositories import user_repository
from app.security import create_access_token, verify_password


@dataclass(frozen=True)
class LoginResult:
    user: User
    access_token: str


class Login:
    def __init__(self, session: AsyncSession, email: str, password: str) -> None:
        self.session = session
        self.email = email.strip().lower()
        self.password = password

    async def __call__(self) -> LoginResult:
        user = await user_repository.find_by_email(self.session, self.email)
        if user is None or not verify_password(self.password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        return LoginResult(user=user, access_token=create_access_token(user.id, user.account_id))
