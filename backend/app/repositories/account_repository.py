from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account, ApiKey
from app.security import hash_api_key


async def find_by_active_api_key(session: AsyncSession, api_key: str) -> Account | None:
    return await session.scalar(
        select(Account)
        .join(ApiKey, ApiKey.account_id == Account.id)
        .where(ApiKey.key_hash == hash_api_key(api_key), ApiKey.revoked_at.is_(None))
    )


async def timezone_of(session: AsyncSession, account_id: int) -> str | None:
    return await session.scalar(select(Account.timezone).where(Account.id == account_id))


async def any_exists(session: AsyncSession) -> bool:
    return await session.scalar(select(exists().select_from(Account)))
