from datetime import UTC, date, datetime

from app.seed.demo_accounts import CampaignProfile
from app.seed.traffic_plan import campaign_hours, hourly_slots

PROFILE = CampaignProfile("Search", "Google Ads", "+15550000001", 0.5, 0.2, 0.25)


def test_converted_threshold_applies_the_conversion_rate_to_answered_calls_only():
    assert PROFILE.missed_threshold() == 0.2
    assert PROFILE.converted_threshold() == 0.4


def test_hourly_slots_cover_a_full_local_day():
    slots = hourly_slots(date(2026, 10, 1), "America/Chicago", now=datetime(2026, 10, 10, tzinfo=UTC))

    assert len(slots) == 24
    assert slots[0].hour_start == datetime(2026, 10, 1, 5, tzinfo=UTC)


def test_hourly_slots_skip_hours_that_have_not_finished_yet():
    now = datetime(2026, 10, 1, 8, 30, tzinfo=UTC)

    slots = hourly_slots(date(2026, 10, 1), "America/Chicago", now=now)

    assert [slot.hour_start.astimezone(UTC).hour for slot in slots] == [5, 6, 7]


def test_campaign_hours_split_each_hour_by_campaign_share():
    slots = hourly_slots(date(2026, 10, 1), "America/Chicago", now=datetime(2026, 10, 10, tzinfo=UTC))[9:10]

    hours = campaign_hours(slots, calls_per_weight=100, campaigns=[(1, PROFILE)])

    assert [hour.call_count for hour in hours] == [round(slots[0].weight * 100 * 0.5)]
