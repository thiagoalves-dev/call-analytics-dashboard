import pytest

from tests.factories import create_account, create_api_key, create_campaign, create_user
from tests.helpers import log_in, send_list_campaigns_request, send_tracking_numbers_request


@pytest.fixture
async def acme(session):
    account = await create_account(session, name="Acme")
    await create_user(session, account, email="manager@acme.test")
    await create_campaign(session, account, name="Acme Radio", tracking_number="+15550000001")
    await create_api_key(session, account, key="acme-key")
    return account


@pytest.fixture
async def summit(session):
    account = await create_account(session, name="Summit")
    await create_campaign(session, account, name="Summit Billboard", tracking_number="+15550000002")
    return account


async def test_rejects_unauthenticated_campaign_requests(client):
    assert (await send_list_campaigns_request(client)).status_code == 401


async def test_rejects_tracking_number_requests_without_an_api_key(client):
    assert (await send_tracking_numbers_request(client, None)).status_code == 401


async def test_lists_only_the_users_own_campaigns(client, acme, summit):
    await log_in(client, "manager@acme.test")

    campaigns = (await send_list_campaigns_request(client)).json()

    assert [campaign["name"] for campaign in campaigns] == ["Acme Radio"]


async def test_lists_only_the_api_keys_own_tracking_numbers(client, acme, summit):
    response = await send_tracking_numbers_request(client, "acme-key")

    assert response.json() == ["+15550000001"]
