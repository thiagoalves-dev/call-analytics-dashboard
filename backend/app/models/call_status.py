from enum import StrEnum

from sqlalchemy import Enum


class CallStatus(StrEnum):
    MISSED = "missed"
    CONNECTED = "connected"
    CONVERTED = "converted"

    def is_converted(self) -> bool:
        return self is CallStatus.CONVERTED


call_status_column_type = Enum(
    CallStatus,
    name="call_status",
    values_callable=lambda statuses: [status.value for status in statuses],
    create_type=False,
)
