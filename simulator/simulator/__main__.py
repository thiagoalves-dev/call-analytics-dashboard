import asyncio
import logging
import random

import httpx

from simulator.config import SimulatorConfig
from simulator.fake_call import fake_call

logger = logging.getLogger("simulator")

HEALTH_CHECK_INTERVAL_SECONDS = 2
IDLE_INTERVAL_SECONDS = 5


async def wait_for_api(client: httpx.AsyncClient) -> None:
    while True:
        try:
            if (await client.get("/api/health")).is_success:
                return
        except httpx.TransportError:
            pass
        logger.info("Waiting for the API")
        await asyncio.sleep(HEALTH_CHECK_INTERVAL_SECONDS)


async def tracking_numbers_by_key(client: httpx.AsyncClient, api_keys: tuple[str, ...]) -> dict[str, list[str]]:
    numbers = {}
    for api_key in api_keys:
        response = await client.get("/api/ingest/tracking-numbers", headers={"X-API-Key": api_key})
        response.raise_for_status()
        numbers[api_key] = response.json()
    return numbers


async def send_call(client: httpx.AsyncClient, api_key: str, tracking_number: str, config: SimulatorConfig) -> None:
    call = fake_call(tracking_number)
    deliveries = 2 if random.random() < config.duplicate_delivery_rate else 1
    for _ in range(deliveries):
        response = await client.post("/api/calls", json=call, headers={"X-API-Key": api_key})
        logger.info(
            "%s %s %s -> %s", call["external_id"], call["tracking_number"], call["status"], response.status_code
        )


async def run(config: SimulatorConfig) -> None:
    async with httpx.AsyncClient(base_url=config.api_url, timeout=10) as client:
        await wait_for_api(client)
        numbers = await tracking_numbers_by_key(client, config.api_keys)
        while True:
            if config.calls_per_second <= 0:
                await asyncio.sleep(IDLE_INTERVAL_SECONDS)
                continue
            await asyncio.sleep(random.expovariate(config.calls_per_second))
            await send_random_call(client, numbers, config)


async def send_random_call(client: httpx.AsyncClient, numbers: dict[str, list[str]], config: SimulatorConfig) -> None:
    api_key = random.choice(config.api_keys)
    try:
        await send_call(client, api_key, random.choice(numbers[api_key]), config)
    except httpx.TransportError as error:
        logger.warning("API unreachable, skipping this call: %r", error)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    asyncio.run(run(SimulatorConfig.from_environment()))


main()
