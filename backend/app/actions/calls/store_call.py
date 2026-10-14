from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import UnprocessableError
from app.models import Account, Call, Campaign
from app.repositories import call_repository, campaign_repository
from app.schemas.call import CallResponse, StoreCallRequest

MAX_CLOCK_SKEW = timedelta(minutes=5)
MAX_LATENESS = timedelta(days=3)


@dataclass(frozen=True)
class StoredCall:
    call: CallResponse
    created: bool


class StoreCall:
    def __init__(self, session: AsyncSession, account: Account, request: StoreCallRequest) -> None:
        self.session = session
        self.account = account
        self.request = request

    async def __call__(self) -> StoredCall:
        self.ensure_start_time_is_acceptable()
        campaign = await self.campaign_for_tracking_number()
        inserted = await call_repository.insert_unless_duplicate(self.session, self.call_values(campaign))
        call = inserted or await self.existing_call()
        await self.session.commit()
        return StoredCall(call=CallResponse.from_models(call, campaign), created=inserted is not None)

    def ensure_start_time_is_acceptable(self) -> None:
        now = datetime.now(UTC)
        if self.request.started_at > now + MAX_CLOCK_SKEW:
            raise UnprocessableError("started_at is in the future")
        if self.request.started_at < now - MAX_LATENESS:
            raise UnprocessableError("started_at is older than 3 days; use the bulk backfill instead")

    async def campaign_for_tracking_number(self) -> Campaign:
        campaign = await campaign_repository.find_by_tracking_number(
            self.session, self.account.id, self.request.tracking_number
        )
        if campaign is None:
            raise UnprocessableError(f"Unknown tracking number {self.request.tracking_number}")
        return campaign

    def call_values(self, campaign: Campaign) -> dict:
        return {
            "account_id": self.account.id,
            "campaign_id": campaign.id,
            "ended_at": self.request.started_at + timedelta(seconds=self.request.duration_seconds),
            **self.request.model_dump(
                include={"external_id", "caller_number", "started_at", "duration_seconds", "status"}
            ),
        }

    async def existing_call(self) -> Call:
        return await call_repository.find_by_external_id(
            self.session, self.account.id, self.request.external_id, self.request.started_at
        )
