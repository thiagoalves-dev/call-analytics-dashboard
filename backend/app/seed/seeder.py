import logging
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.config import Settings
from app.models import Account, ApiKey, Campaign, User
from app.security import hash_api_key, hash_password
from app.seed.demo_accounts import DEMO_ACCOUNTS, DemoAccount
from app.seed.traffic_plan import CampaignHour, campaign_hours, hourly_slots
from app.support.time import local_date, local_midnight

logger = logging.getLogger(__name__)

GENERATE_CALLS_SQL = text((Path(__file__).parent / "generate_calls.sql").read_text())
ROLL_UP_CALLS_SQL = text((Path(__file__).parent / "roll_up_calls.sql").read_text())
ONE_DAY = timedelta(days=1)


class Seeder:
    def __init__(self, engine: AsyncEngine, settings: Settings) -> None:
        self.engine = engine
        self.settings = settings
        self.now = datetime.now(UTC)

    async def __call__(self) -> None:
        async with AsyncSession(self.engine, expire_on_commit=False) as session:
            if await session.scalar(select(func.count()).select_from(Account)):
                logger.info("Database already seeded, skipping")
                return
            for demo_account in DEMO_ACCOUNTS:
                await self.seed_account(session, demo_account)
        await self.analyze()
        logger.info("Seed complete")

    async def seed_account(self, session: AsyncSession, demo_account: DemoAccount) -> None:
        account = await self.create_account(session, demo_account)
        campaigns = await self.create_campaigns(session, account, demo_account)
        await session.commit()
        calls_per_weight = self.settings.seed_calls_per_account / self.total_weight(demo_account.timezone)
        for day in self.days(demo_account.timezone):
            hours = campaign_hours(hourly_slots(day, demo_account.timezone, self.now), calls_per_weight, campaigns)
            await self.insert_calls(session, account.id, hours)
            await self.roll_up_day(session, account.id, day, demo_account.timezone)
            logger.info("%s: seeded %s", demo_account.name, day)

    async def create_account(self, session: AsyncSession, demo_account: DemoAccount) -> Account:
        account = Account(name=demo_account.name, timezone=demo_account.timezone)
        session.add(account)
        await session.flush()
        session.add(
            User(
                account_id=account.id,
                email=demo_account.user_email,
                name=demo_account.user_name,
                password_hash=hash_password(demo_account.user_password),
            )
        )
        api_key = getattr(self.settings, demo_account.api_key_setting)
        session.add(ApiKey(account_id=account.id, name="Telephony provider", key_hash=hash_api_key(api_key)))
        return account

    async def create_campaigns(self, session: AsyncSession, account: Account, demo_account: DemoAccount) -> list:
        campaigns = []
        for profile in demo_account.campaigns:
            campaign = Campaign(
                account_id=account.id, name=profile.name, source=profile.source, tracking_number=profile.tracking_number
            )
            session.add(campaign)
            await session.flush()
            campaigns.append((campaign.id, profile))
        return campaigns

    def days(self, timezone: str) -> list:
        today = local_date(self.now, timezone)
        return [today - offset * ONE_DAY for offset in reversed(range(self.settings.seed_days))]

    def total_weight(self, timezone: str) -> float:
        return sum(slot.weight for day in self.days(timezone) for slot in hourly_slots(day, timezone, self.now))

    async def insert_calls(self, session: AsyncSession, account_id: int, hours: list[CampaignHour]) -> None:
        await session.execute(
            GENERATE_CALLS_SQL,
            {
                "account_id": account_id,
                "hour_starts": [hour.hour_start for hour in hours],
                "campaign_ids": [hour.campaign_id for hour in hours],
                "call_counts": [hour.call_count for hour in hours],
                "missed_thresholds": [hour.profile.missed_threshold() for hour in hours],
                "converted_thresholds": [hour.profile.converted_threshold() for hour in hours],
            },
        )
        await session.commit()

    async def roll_up_day(self, session: AsyncSession, account_id: int, day: date, timezone: str) -> None:
        start, end = local_midnight(day, timezone), local_midnight(day + ONE_DAY, timezone)
        await session.execute(ROLL_UP_CALLS_SQL, {"account_id": account_id, "start": start, "end": end})
        await session.commit()

    async def analyze(self) -> None:
        async with self.engine.connect() as connection:
            autocommit = await connection.execution_options(isolation_level="AUTOCOMMIT")
            await autocommit.execute(text("ANALYZE calls, call_stats_hourly"))
