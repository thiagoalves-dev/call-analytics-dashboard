from httpx import AsyncClient, Response

from tests.factories import DEFAULT_PASSWORD


async def send_login_request(client: AsyncClient, email: str, password: str = DEFAULT_PASSWORD) -> Response:
    return await client.post("/api/auth/login", json={"email": email, "password": password})


async def log_in(client: AsyncClient, email: str) -> None:
    (await send_login_request(client, email)).raise_for_status()


async def send_me_request(client: AsyncClient) -> Response:
    return await client.get("/api/auth/me")


async def send_store_call_request(client: AsyncClient, payload: dict, api_key: str | None) -> Response:
    headers = {"X-API-Key": api_key} if api_key else {}
    return await client.post("/api/calls", json=payload, headers=headers)


async def send_list_calls_request(client: AsyncClient, params: dict | None = None) -> Response:
    return await client.get("/api/calls", params=params)


async def send_volume_request(client: AsyncClient, params: dict | None = None) -> Response:
    return await client.get("/api/stats/volume", params=params)


async def send_conversion_request(client: AsyncClient, params: dict | None = None) -> Response:
    return await client.get("/api/stats/conversion", params=params)


async def send_list_campaigns_request(client: AsyncClient) -> Response:
    return await client.get("/api/campaigns")


async def send_tracking_numbers_request(client: AsyncClient, api_key: str | None) -> Response:
    headers = {"X-API-Key": api_key} if api_key else {}
    return await client.get("/api/ingest/tracking-numbers", headers=headers)
