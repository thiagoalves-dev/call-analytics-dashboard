from datetime import UTC, datetime

import pytest

from app.models import CallStatus
from tests.factories import create_account, create_call, create_campaign, create_user
from tests.helpers import log_in, send_volume_request


@pytest.fixture
async def acme(session):
    account = await create_account(session, name="Acme", timezone="America/Chicago")
    await create_user(session, account, email="manager@acme.test")
    return account


@pytest.fixture
async def campaign(session, acme):
    return await create_campaign(session, acme)


def counts_by_bucket(response) -> dict[str, int]:
    return {point["bucket"]: point["total"] for point in response.json()["points"]}


async def test_rejects_unauthenticated_requests(client):
    assert (await send_volume_request(client)).status_code == 401


async def test_rejects_an_hourly_view_longer_than_31_days(client, acme):
    await log_in(client, "manager@acme.test")
    params = {"granularity": "hour", "from": "2026-08-01T00:00:00Z", "to": "2026-10-01T00:00:00Z"}

    response = await send_volume_request(client, params)

    assert response.status_code == 422
    assert "daily view" in response.json()["detail"]


async def test_rejects_an_unknown_granularity(client, acme):
    await log_in(client, "manager@acme.test")

    assert (await send_volume_request(client, {"granularity": "minute"})).status_code == 422


async def test_hourly_view_counts_calls_per_hour_and_fills_empty_hours(client, session, campaign):
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 10, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 50, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 1, 11, 5, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {"granularity": "hour", "from": "2026-10-01T09:00:00Z", "to": "2026-10-01T12:00:00Z"}

    response = await send_volume_request(client, params)

    assert counts_by_bucket(response) == {
        "2026-10-01T09:00:00Z": 2,
        "2026-10-01T10:00:00Z": 0,
        "2026-10-01T11:00:00Z": 1,
    }


async def test_daily_view_cuts_days_at_the_accounts_local_midnight(client, session, campaign):
    await create_call(session, campaign, datetime(2026, 10, 2, 4, 30, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 2, 5, 30, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {"granularity": "day", "from": "2026-10-01T05:00:00Z", "to": "2026-10-03T05:00:00Z"}

    response = await send_volume_request(client, params)

    assert counts_by_bucket(response) == {"2026-10-01T00:00:00-05:00": 1, "2026-10-02T00:00:00-05:00": 1}


async def test_daily_view_handles_the_day_daylight_saving_time_ends(client, session, campaign):
    await create_call(session, campaign, datetime(2026, 11, 2, 5, 30, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {"granularity": "day", "from": "2026-11-01T05:00:00Z", "to": "2026-11-03T06:00:00Z"}

    response = await send_volume_request(client, params)

    assert counts_by_bucket(response) == {"2026-11-01T00:00:00-05:00": 1, "2026-11-02T00:00:00-06:00": 0}


async def test_outcome_filter_keeps_only_the_selected_outcomes(client, session, campaign):
    await create_call(session, campaign, datetime(2026, 10, 1, 9, tzinfo=UTC), CallStatus.MISSED)
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 5, tzinfo=UTC), CallStatus.CONVERTED)
    await log_in(client, "manager@acme.test")
    params = {"granularity": "hour", "from": "2026-10-01T09:00:00Z", "to": "2026-10-01T10:00:00Z", "status": "missed"}

    point = (await send_volume_request(client, params)).json()["points"][0]

    assert (point["total"], point["missed"], point["converted"]) == (1, 1, 0)


async def test_campaign_filter_keeps_only_the_selected_campaigns(client, session, acme, campaign):
    radio = await create_campaign(session, acme, name="Radio", tracking_number="+15550000002")
    await create_call(session, campaign, datetime(2026, 10, 1, 9, tzinfo=UTC))
    await create_call(session, radio, datetime(2026, 10, 1, 9, 5, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {
        "granularity": "hour",
        "from": "2026-10-01T09:00:00Z",
        "to": "2026-10-01T10:00:00Z",
        "campaign_id": radio.id,
    }

    assert counts_by_bucket(await send_volume_request(client, params)) == {"2026-10-01T09:00:00Z": 1}


async def test_never_counts_another_accounts_calls(client, session, acme):
    other_campaign = await create_campaign(
        session, await create_account(session, name="Summit"), tracking_number="+1999"
    )
    await create_call(session, other_campaign, datetime(2026, 10, 1, 9, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {"granularity": "hour", "from": "2026-10-01T09:00:00Z", "to": "2026-10-01T10:00:00Z"}

    assert counts_by_bucket(await send_volume_request(client, params)) == {"2026-10-01T09:00:00Z": 0}
