import random
import uuid
from datetime import UTC, datetime, timedelta

OUTCOME_WEIGHTS = {"missed": 0.16, "connected": 0.58, "converted": 0.26}
DURATION_RANGE_SECONDS = {"missed": (0, 0), "connected": (20, 420), "converted": (120, 900)}


def fake_call(tracking_number: str) -> dict:
    status = random.choices(list(OUTCOME_WEIGHTS), weights=list(OUTCOME_WEIGHTS.values()))[0]
    duration_seconds = random.randint(*DURATION_RANGE_SECONDS[status])
    return {
        "external_id": f"sim-{uuid.uuid4()}",
        "tracking_number": tracking_number,
        "caller_number": f"+1555{random.randint(0, 9_999_999):07d}",
        "started_at": (datetime.now(UTC) - timedelta(seconds=duration_seconds)).isoformat(),
        "duration_seconds": duration_seconds,
        "status": status,
    }
