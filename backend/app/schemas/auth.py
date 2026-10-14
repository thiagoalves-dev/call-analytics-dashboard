from pydantic import BaseModel

from app.models import Account, User


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    account_id: int
    account_name: str
    timezone: str

    @classmethod
    def from_models(cls, user: User, account: Account) -> "UserResponse":
        return cls(
            id=user.id,
            email=user.email,
            name=user.name,
            account_id=account.id,
            account_name=account.name,
            timezone=account.timezone,
        )
