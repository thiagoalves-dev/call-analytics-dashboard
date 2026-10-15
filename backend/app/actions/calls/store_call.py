from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, UnprocessableError
from app.models import Account, Call, Campaign
from app.repositories import call_repository, call_stats_repository, campaign_repository
from app.schemas.call import CallResponse, StoreCallRequest
from app.services.broadcaster import Broadcaster

MAX_CLOCK_SKEW = timedelta(minutes=5)
MAX_LATENESS = timedelta(days=3)


@dataclass(frozen=True)
class StoredCall:
    call: CallResponse
    created: bool

    def status_code(self) -> int:
        return status.HTTP_201_CREATED if self.created else status.HTTP_200_OK


class StoreCall:
    def __init__(
        self, session: AsyncSession, broadcaster: Broadcaster, account: Account, request: StoreCallRequest
    ) -> None:
        self.session = session
        self.broadcaster = broadcaster
        self.account = account
        self.request = request

    async def __call__(self) -> StoredCall:
        self.ensure_start_time_is_acceptable()
        campaign = await self.campaign_for_tracking_number()
        inserted = await call_repository.insert_unless_duplicate(self.session, self.call_values(campaign))
        if inserted is None:
            return await self.previously_stored_call()
        await call_stats_repository.record_call(self.session, inserted)
        await self.session.commit()
        stored = StoredCall(call=CallResponse.from_models(inserted, campaign), created=True)
        await self.broadcaster.publish(self.account.id, stored.call.model_dump_json())
        return stored

    def ensure_start_time_is_acceptable(self) -> None:
        now = datetime.now(UTC)
        if self.request.started_at > now + MAX_CLOCK_SKEW:
            raise UnprocessableError("started_at is in the future")
        if self.request.started_at < now - MAX_LATENESS:
            raise UnprocessableError(
                f"started_at is older than {MAX_LATENESS.days} days; use the bulk backfill instead"
            )

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

    async def previously_stored_call(self) -> StoredCall:
        call, campaign = await call_repository.find_with_campaign_by_external_id(
            self.session, self.account.id, self.request.external_id, self.request.started_at
        )
        await self.session.commit()
        if not self.matches_request(call, campaign):
            raise ConflictError(
                f"external_id {self.request.external_id} was already stored with different call data; "
                "a retry must repeat the original delivery"
            )
        return StoredCall(call=CallResponse.from_models(call, campaign), created=False)

    def matches_request(self, call: Call, campaign: Campaign) -> bool:
        stored = (campaign.tracking_number, call.caller_number, call.started_at, call.duration_seconds, call.status)
        request = self.request
        retried = (
            request.tracking_number,
            request.caller_number,
            request.started_at,
            request.duration_seconds,
            request.status,
        )
        return stored == retried
