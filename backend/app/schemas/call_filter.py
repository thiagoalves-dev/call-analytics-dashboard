from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.models import CallStatus


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
