from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field

from app.models import Call, CallStatus, Campaign

MAX_CALL_DURATION_SECONDS = 24 * 60 * 60


class StoreCallRequest(BaseModel):
    external_id: str = Field(min_length=1, max_length=64)
    tracking_number: str = Field(min_length=1, max_length=20)
    caller_number: str = Field(min_length=1, max_length=20)
    started_at: AwareDatetime
    duration_seconds: int = Field(ge=0, le=MAX_CALL_DURATION_SECONDS)
    status: CallStatus


class CallResponse(BaseModel):
    id: int
    external_id: str | None
    campaign_id: int
    campaign_name: str
    source: str
    caller_number: str
    started_at: datetime
    duration_seconds: int
    ended_at: datetime
    status: CallStatus

    @classmethod
    def from_models(cls, call: Call, campaign: Campaign) -> "CallResponse":
        return cls(
            id=call.id,
            external_id=call.external_id,
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            source=campaign.source,
            caller_number=call.caller_number,
            started_at=call.started_at,
            duration_seconds=call.duration_seconds,
            ended_at=call.ended_at,
            status=call.status,
        )
