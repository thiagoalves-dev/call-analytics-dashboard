import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.seed.demo_accounts import CampaignProfile
from app.support.time import local_midnight

ONE_HOUR = timedelta(hours=1)
ONE_DAY = timedelta(days=1)

HOUR_OF_DAY_WEIGHTS = (
    0.05,
    0.03,
    0.02,
    0.02,
    0.03,
    0.08,
    0.25,
    0.60,
    1.00,
    1.30,
    1.40,
    1.35,
    1.20,
    1.25,
    1.30,
    1.25,
    1.10,
    0.90,
    0.60,
    0.40,
    0.30,
    0.20,
    0.12,
    0.08,
)
DAY_OF_WEEK_WEIGHTS = (1.10, 1.05, 1.00, 1.00, 0.95, 0.55, 0.35)
HOURLY_NOISE = (0.8, 1.2)


@dataclass(frozen=True)
class HourlySlot:
    hour_start: datetime
    weight: float


@dataclass(frozen=True)
class CampaignHour:
    hour_start: datetime
    campaign_id: int
    call_count: int
    profile: CampaignProfile


def hourly_slots(day: date, timezone: str, now: datetime) -> list[HourlySlot]:
    hour_start = local_midnight(day, timezone).astimezone(UTC)
    next_midnight = local_midnight(day + ONE_DAY, timezone).astimezone(UTC)
    slots = []
    while hour_start < next_midnight and hour_start + ONE_HOUR <= now:
        local_hour = hour_start.astimezone(ZoneInfo(timezone)).hour
        slots.append(HourlySlot(hour_start, slot_weight(local_hour, day)))
        hour_start += ONE_HOUR
    return slots


def slot_weight(hour: int, day: date) -> float:
    return HOUR_OF_DAY_WEIGHTS[hour] * DAY_OF_WEEK_WEIGHTS[day.weekday()] * random.uniform(*HOURLY_NOISE)


def campaign_hours(
    slots: list[HourlySlot], calls_per_weight: float, campaigns: list[tuple[int, CampaignProfile]]
) -> list[CampaignHour]:
    return [
        CampaignHour(
            slot.hour_start, campaign_id, round(slot.weight * calls_per_weight * profile.share_of_calls), profile
        )
        for slot in slots
        for campaign_id, profile in campaigns
    ]
