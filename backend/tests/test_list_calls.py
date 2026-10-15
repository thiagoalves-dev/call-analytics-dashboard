from datetime import UTC, datetime

import pytest

from app.models import CallStatus
from tests.factories import create_account, create_call, create_campaign, create_user
from tests.helpers import log_in, send_list_calls_request

RANGE = {"from": "2026-10-01T00:00:00Z", "to": "2026-10-02T00:00:00Z"}


@pytest.fixture
async def acme(session):
    account = await create_account(session, name="Acme")
    await create_user(session, account, email="manager@acme.test")
    return account


async def test_rejects_unauthenticated_requests(client):
    assert (await send_list_calls_request(client)).status_code == 401


async def test_rejects_a_range_that_ends_before_it_starts(client, acme):
    await log_in(client, "manager@acme.test")
    params = {"from": "2026-10-02T00:00:00Z", "to": "2026-10-01T00:00:00Z"}

    response = await send_list_calls_request(client, params)

    assert response.status_code == 422
    assert response.json() == {"detail": "from must be before to"}


async def test_rejects_a_range_longer_than_366_days(client, acme):
    await log_in(client, "manager@acme.test")
    params = {"from": "2025-01-01T00:00:00Z", "to": "2026-10-01T00:00:00Z"}

    response = await send_list_calls_request(client, params)

    assert response.status_code == 422
    assert response.json() == {"detail": "The date range is limited to 366 days"}


async def test_rejects_a_limit_above_the_maximum(client, acme):
    await log_in(client, "manager@acme.test")

    assert (await send_list_calls_request(client, RANGE | {"limit": 500})).status_code == 422


async def test_returns_the_newest_calls_first(client, session, acme):
    campaign = await create_campaign(session, acme)
    await create_call(session, campaign, datetime(2026, 10, 1, 9, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 1, 15, tzinfo=UTC))
    await log_in(client, "manager@acme.test")

    calls = (await send_list_calls_request(client, RANGE)).json()

    assert [call["started_at"] for call in calls] == ["2026-10-01T15:00:00Z", "2026-10-01T09:00:00Z"]


async def test_orders_by_when_the_call_ended(client, session, acme):
    campaign = await create_campaign(session, acme)
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 0, tzinfo=UTC), duration_seconds=600)
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 5, tzinfo=UTC), CallStatus.MISSED)
    await log_in(client, "manager@acme.test")

    calls = (await send_list_calls_request(client, RANGE)).json()

    assert [call["ended_at"] for call in calls] == ["2026-10-01T09:10:00Z", "2026-10-01T09:05:00Z"]


async def test_uses_the_exact_range_without_rounding_to_whole_hours(client, session, acme):
    campaign = await create_campaign(session, acme)
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 10, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 1, 9, 40, tzinfo=UTC))
    await create_call(session, campaign, datetime(2026, 10, 1, 10, 20, tzinfo=UTC))
    await log_in(client, "manager@acme.test")
    params = {"from": "2026-10-01T09:30:00Z", "to": "2026-10-01T10:15:00Z"}

    calls = (await send_list_calls_request(client, params)).json()

    assert [call["started_at"] for call in calls] == ["2026-10-01T09:40:00Z"]


async def test_filters_by_campaign_and_outcome(client, session, acme):
    google = await create_campaign(session, acme, name="Google", tracking_number="+15550000001")
    radio = await create_campaign(session, acme, name="Radio", tracking_number="+15550000002")
    await create_call(session, google, datetime(2026, 10, 1, 9, tzinfo=UTC), CallStatus.MISSED)
    await create_call(session, google, datetime(2026, 10, 1, 10, tzinfo=UTC), CallStatus.CONVERTED)
    await create_call(session, radio, datetime(2026, 10, 1, 11, tzinfo=UTC), CallStatus.CONVERTED)
    await log_in(client, "manager@acme.test")

    calls = (await send_list_calls_request(client, RANGE | {"campaign_id": google.id, "status": "converted"})).json()

    assert [(call["campaign_name"], call["status"]) for call in calls] == [("Google", "converted")]


async def test_never_returns_another_accounts_calls(client, session, acme):
    other_account = await create_account(session, name="Summit")
    other_campaign = await create_campaign(session, other_account, tracking_number="+15550000009")
    await create_call(session, other_campaign, datetime(2026, 10, 1, 9, tzinfo=UTC))
    await log_in(client, "manager@acme.test")

    assert (await send_list_calls_request(client, RANGE)).json() == []
