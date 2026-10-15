from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthenticationError
from app.repositories import user_repository
from app.schemas.auth import UserResponse
from app.security import create_access_token, hash_password, verify_password

DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-unknown-emails")


@dataclass(frozen=True)
class LoginResult:
    user: UserResponse
    access_token: str


class Login:
    def __init__(self, session: AsyncSession, email: str, password: str) -> None:
        self.session = session
        self.email = email.strip().lower()
        self.password = password

    async def __call__(self) -> LoginResult:
        found = await user_repository.find_with_account_by_email(self.session, self.email)
        password_hash = found.User.password_hash if found else DUMMY_PASSWORD_HASH
        if not verify_password(self.password, password_hash) or found is None:
            raise AuthenticationError("Invalid email or password")
        return LoginResult(
            user=UserResponse.from_models(found.User, found.Account),
            access_token=create_access_token(found.User.id, found.Account.id),
        )
