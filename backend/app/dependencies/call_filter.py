from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Query, status
from pydantic import AwareDatetime

from app.models import CallStatus

DEFAULT_RANGE = timedelta(days=7)
MAX_RANGE = timedelta(days=366)


@dataclass(frozen=True)
class CallFilter:
    start: datetime
    end: datetime
    campaign_ids: list[int] = field(default_factory=list)
    statuses: list[CallStatus] = field(default_factory=list)

    def included_statuses(self) -> list[CallStatus]:
        return self.statuses or list(CallStatus)

    def spans_more_than(self, duration: timedelta) -> bool:
        return self.end - self.start > duration


def call_filter(
    start: Annotated[AwareDatetime | None, Query(alias="from")] = None,
    end: Annotated[AwareDatetime | None, Query(alias="to")] = None,
    campaign_id: Annotated[list[int] | None, Query()] = None,
    call_status: Annotated[list[CallStatus] | None, Query(alias="status")] = None,
) -> CallFilter:
    end = end or datetime.now(UTC)
    start = start or end - DEFAULT_RANGE
    ensure_valid_range(start, end)
    return CallFilter(
        start=start, end=end, campaign_ids=sorted(set(campaign_id or [])), statuses=sorted(set(call_status or []))
    )


def ensure_valid_range(start: datetime, end: datetime) -> None:
    if start >= end:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "from must be before to")
    if end - start > MAX_RANGE:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "The date range is limited to 366 days")


CallFilterQuery = Annotated[CallFilter, Depends(call_filter)]
