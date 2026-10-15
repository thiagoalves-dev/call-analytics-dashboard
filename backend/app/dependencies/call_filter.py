from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, Query
from pydantic import AwareDatetime

from app.exceptions import UnprocessableError
from app.models import CallStatus
from app.schemas.call_filter import CallFilter

DEFAULT_RANGE = timedelta(days=7)
MAX_RANGE = timedelta(days=366)


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
        raise UnprocessableError("from must be before to")
    if end - start > MAX_RANGE:
        raise UnprocessableError(f"The date range is limited to {MAX_RANGE.days} days")


CallFilterQuery = Annotated[CallFilter, Depends(call_filter)]
