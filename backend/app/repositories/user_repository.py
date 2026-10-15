from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account, User


async def find_with_account_by_email(session: AsyncSession, email: str) -> Row[tuple[User, Account]] | None:
    query = select(User, Account).join(Account, Account.id == User.account_id).where(User.email == email)
    return (await session.execute(query)).first()


async def find_with_account(session: AsyncSession, user_id: int) -> Row[tuple[User, Account]] | None:
    query = select(User, Account).join(Account, Account.id == User.account_id).where(User.id == user_id)
    return (await session.execute(query)).first()
