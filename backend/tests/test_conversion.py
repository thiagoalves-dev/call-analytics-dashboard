from datetime import UTC, datetime

import pytest

from app.models import CallStatus
from tests.factories import create_account, create_call, create_campaign, create_user
from tests.helpers import log_in, send_conversion_request

RANGE = {"from": "2026-10-01T00:00:00Z", "to": "2026-10-02T00:00:00Z"}
NINE_AM = datetime(2026, 10, 1, 9, tzinfo=UTC)


@pytest.fixture
async def acme(session):
    account = await create_account(session, name="Acme")
    await create_user(session, account, email="manager@acme.test")
    return account


async def create_calls(session, campaign, *statuses: CallStatus) -> None:
    for call_status in statuses:
        await create_call(session, campaign, NINE_AM, call_status)


async def test_rejects_unauthenticated_requests(client):
    assert (await send_conversion_request(client)).status_code == 401


async def test_rejects_an_unknown_grouping(client, acme):
    await log_in(client, "manager@acme.test")

    assert (await send_conversion_request(client, RANGE | {"group_by": "caller"})).status_code == 422


async def test_conversion_rate_is_converted_calls_over_all_calls(client, session, acme):
    campaign = await create_campaign(session, acme, name="Google")
    await create_calls(
        session, campaign, CallStatus.CONVERTED, CallStatus.CONNECTED, CallStatus.MISSED, CallStatus.MISSED
    )
    await log_in(client, "manager@acme.test")

    row = (await send_conversion_request(client, RANGE)).json()["rows"][0]

    assert (row["label"], row["calls"], row["converted"], row["conversion_rate"]) == ("Google", 4, 1, 0.25)


async def test_groups_campaigns_by_marketing_source(client, session, acme):
    search = await create_campaign(session, acme, name="Search", source="Google Ads", tracking_number="+15550000001")
    display = await create_campaign(session, acme, name="Display", source="Google Ads", tracking_number="+15550000002")
    await create_calls(session, search, CallStatus.CONVERTED)
    await create_calls(session, display, CallStatus.MISSED)
    await log_in(client, "manager@acme.test")

    rows = (await send_conversion_request(client, RANGE | {"group_by": "source"})).json()["rows"]

    assert [(row["label"], row["calls"], row["conversion_rate"]) for row in rows] == [("Google Ads", 2, 0.5)]


async def test_ignores_the_outcome_filter(client, session, acme):
    campaign = await create_campaign(session, acme)
    await create_calls(session, campaign, CallStatus.CONVERTED, CallStatus.MISSED)
    await log_in(client, "manager@acme.test")

    row = (await send_conversion_request(client, RANGE | {"status": "missed"})).json()["rows"][0]

    assert row["conversion_rate"] == 0.5


async def test_sorts_campaigns_by_call_volume(client, session, acme):
    small = await create_campaign(session, acme, name="Small", tracking_number="+15550000001")
    large = await create_campaign(session, acme, name="Large", tracking_number="+15550000002")
    await create_calls(session, small, CallStatus.CONNECTED)
    await create_calls(session, large, CallStatus.CONNECTED, CallStatus.CONNECTED)
    await log_in(client, "manager@acme.test")

    rows = (await send_conversion_request(client, RANGE)).json()["rows"]

    assert [row["label"] for row in rows] == ["Large", "Small"]


async def test_never_includes_another_accounts_campaigns(client, session, acme):
    other_campaign = await create_campaign(
        session, await create_account(session, name="Summit"), tracking_number="+1999"
    )
    await create_calls(session, other_campaign, CallStatus.CONVERTED)
    await log_in(client, "manager@acme.test")

    assert (await send_conversion_request(client, RANGE)).json()["rows"] == []
