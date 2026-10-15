from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AuthenticationError
from app.repositories import user_repository
from app.schemas.auth import UserResponse


class ShowCurrentUser:
    def __init__(self, session: AsyncSession, user_id: int) -> None:
        self.session = session
        self.user_id = user_id

    async def __call__(self) -> UserResponse:
        found = await user_repository.find_with_account(self.session, self.user_id)
        if found is None:
            raise AuthenticationError("Invalid or expired session")
        return UserResponse.from_models(found.User, found.Account)
