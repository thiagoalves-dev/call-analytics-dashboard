from datetime import UTC, datetime, timedelta

import jwt

from app.config import get_settings
from tests.factories import create_account, create_user
from tests.helpers import log_in, send_login_request, send_me_request

FORGING_SECRET = "a-different-secret-that-is-long-enough"


async def test_rejects_unauthenticated_requests(client):
    assert (await send_me_request(client)).status_code == 401


async def test_rejects_a_tampered_session_cookie(client, session):
    account = await create_account(session)
    user = await create_user(session, account)
    forged = jwt.encode({"sub": str(user.id), "account_id": account.id}, FORGING_SECRET, algorithm="HS256")
    client.cookies.set(get_settings().cookie_name, forged)

    assert (await send_me_request(client)).status_code == 401


async def test_rejects_an_expired_session_cookie(client, session):
    account = await create_account(session)
    user = await create_user(session, account)
    expired_at = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {"sub": str(user.id), "account_id": account.id, "exp": expired_at}, get_settings().jwt_secret, "HS256"
    )
    client.cookies.set(get_settings().cookie_name, token)

    assert (await send_me_request(client)).status_code == 401


async def test_rejects_a_wrong_password(client, session):
    await create_user(session, await create_account(session), email="manager@acme.test")

    response = await send_login_request(client, "manager@acme.test", "wrong-password")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


async def test_rejects_an_unknown_email_with_the_same_message(client):
    response = await send_login_request(client, "nobody@acme.test")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


async def test_login_sets_an_http_only_session_cookie(client, session):
    await create_user(session, await create_account(session), email="manager@acme.test")

    response = await send_login_request(client, "  Manager@Acme.test ")

    assert response.status_code == 200
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=lax" in response.headers["set-cookie"].lower()


async def test_me_returns_the_user_and_their_account(client, session):
    account = await create_account(session, name="Acme", timezone="America/Chicago")
    await create_user(session, account, email="manager@acme.test")
    await log_in(client, "manager@acme.test")

    body = (await send_me_request(client)).json()

    assert body["email"] == "manager@acme.test"
    assert body["account_name"] == "Acme"
    assert body["timezone"] == "America/Chicago"


async def test_logout_clears_the_session(client, session):
    await create_user(session, await create_account(session), email="manager@acme.test")
    await log_in(client, "manager@acme.test")

    await client.post("/api/auth/logout")

    assert (await send_me_request(client)).status_code == 401
