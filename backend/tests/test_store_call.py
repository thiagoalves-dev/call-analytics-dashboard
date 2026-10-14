import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.models import Call
from tests.factories import create_account, create_api_key, create_campaign
from tests.helpers import send_store_call_request


def call_payload(**overrides) -> dict:
    payload = {
        "external_id": "provider-call-1",
        "tracking_number": "+15550000001",
        "caller_number": "+15557654321",
        "started_at": (datetime.now(UTC) - timedelta(minutes=3)).isoformat(),
        "duration_seconds": 95,
        "status": "converted",
    }
    return payload | overrides


@pytest.fixture
async def acme(session):
    account = await create_account(session, name="Acme")
    await create_campaign(session, account, tracking_number="+15550000001")
    return account


@pytest.fixture
async def api_key(session, acme):
    return await create_api_key(session, acme, key="acme-key")


async def count_calls(session) -> int:
    return await session.scalar(select(func.count()).select_from(Call))


async def test_rejects_a_request_without_an_api_key(client, api_key):
    assert (await send_store_call_request(client, call_payload(), None)).status_code == 401


async def test_rejects_an_unknown_api_key(client, api_key):
    assert (await send_store_call_request(client, call_payload(), "not-a-key")).status_code == 401


async def test_rejects_a_revoked_api_key(client, session, acme):
    await create_api_key(session, acme, key="old-key", revoked_at=datetime.now(UTC))

    assert (await send_store_call_request(client, call_payload(), "old-key")).status_code == 401


async def test_rejects_an_unknown_tracking_number(client, api_key):
    response = await send_store_call_request(client, call_payload(tracking_number="+15559999999"), api_key)

    assert response.status_code == 422
    assert "Unknown tracking number" in response.json()["detail"]


async def test_rejects_another_accounts_tracking_number(client, session, api_key):
    other_account = await create_account(session, name="Summit")
    await create_campaign(session, other_account, tracking_number="+15550000002")

    response = await send_store_call_request(client, call_payload(tracking_number="+15550000002"), api_key)

    assert response.status_code == 422


async def test_rejects_a_call_from_the_future(client, api_key):
    started_at = (datetime.now(UTC) + timedelta(hours=1)).isoformat()

    assert (await send_store_call_request(client, call_payload(started_at=started_at), api_key)).status_code == 422


async def test_rejects_a_call_older_than_the_aggregation_window(client, api_key):
    started_at = (datetime.now(UTC) - timedelta(days=4)).isoformat()

    assert (await send_store_call_request(client, call_payload(started_at=started_at), api_key)).status_code == 422


async def test_rejects_a_start_time_without_a_timezone(client, api_key):
    response = await send_store_call_request(client, call_payload(started_at="2026-10-13T10:00:00"), api_key)

    assert response.status_code == 422


async def test_rejects_an_unknown_status(client, api_key):
    assert (await send_store_call_request(client, call_payload(status="voicemail"), api_key)).status_code == 422


async def test_stores_the_call_under_the_api_keys_account(client, session, acme, api_key):
    response = await send_store_call_request(client, call_payload(), api_key)

    assert response.status_code == 201
    stored = await session.scalar(select(Call))
    assert stored.account_id == acme.id
    assert stored.external_id == "provider-call-1"


async def test_publishes_the_new_call_to_the_accounts_live_feed(client, broadcaster, acme, api_key):
    subscriber = broadcaster.subscribe(acme.id)
    try:
        await send_store_call_request(client, call_payload(), api_key)
        payload = await asyncio.wait_for(subscriber.queue.get(), timeout=2)
    finally:
        broadcaster.unsubscribe(acme.id, subscriber)

    assert '"external_id":"provider-call-1"' in payload


async def test_a_retried_delivery_is_stored_once_and_returns_200(client, session, api_key):
    payload = call_payload()
    first = await send_store_call_request(client, payload, api_key)
    retry = await send_store_call_request(client, payload, api_key)

    assert (first.status_code, retry.status_code) == (201, 200)
    assert retry.json()["id"] == first.json()["id"]
    assert await count_calls(session) == 1
