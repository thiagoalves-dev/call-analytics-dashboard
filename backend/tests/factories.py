from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Account, ApiKey, Call, CallStatus, Campaign, User
from app.repositories import call_stats_repository
from app.security import hash_api_key, hash_password

DEFAULT_PASSWORD = "correct-password"


async def create_account(session: AsyncSession, name: str = "Acme", timezone: str = "America/Chicago") -> Account:
    account = Account(name=name, timezone=timezone)
    session.add(account)
    await session.commit()
    return account


async def create_user(session: AsyncSession, account: Account, email: str = "manager@acme.test") -> User:
    user = User(account_id=account.id, email=email, name="Manager", password_hash=hash_password(DEFAULT_PASSWORD))
    session.add(user)
    await session.commit()
    return user


async def create_api_key(
    session: AsyncSession, account: Account, key: str = "test-key", revoked_at: datetime | None = None
) -> str:
    session.add(ApiKey(account_id=account.id, name="Test", key_hash=hash_api_key(key), revoked_at=revoked_at))
    await session.commit()
    return key


async def create_campaign(
    session: AsyncSession,
    account: Account,
    name: str = "Google Search",
    source: str = "Google Ads",
    tracking_number: str = "+15550000001",
) -> Campaign:
    campaign = Campaign(account_id=account.id, name=name, source=source, tracking_number=tracking_number)
    session.add(campaign)
    await session.commit()
    return campaign


async def create_call(
    session: AsyncSession,
    campaign: Campaign,
    started_at: datetime,
    status: CallStatus = CallStatus.CONNECTED,
    duration_seconds: int | None = None,
) -> Call:
    call = build_call(
        campaign, started_at, status, default_duration(status) if duration_seconds is None else duration_seconds
    )
    session.add(call)
    await session.flush()
    await call_stats_repository.record_call(session, call)
    await session.commit()
    return call


def build_call(campaign: Campaign, started_at: datetime, status: CallStatus, duration_seconds: int) -> Call:
    return Call(
        account_id=campaign.account_id,
        campaign_id=campaign.id,
        caller_number="+15551234567",
        started_at=started_at,
        duration_seconds=duration_seconds,
        ended_at=started_at + timedelta(seconds=duration_seconds),
        status=status,
    )


def default_duration(status: CallStatus) -> int:
    return 0 if status is CallStatus.MISSED else 120
