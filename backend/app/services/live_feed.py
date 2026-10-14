import asyncio
from collections.abc import AsyncIterator

from fastapi import Request

from app.services.broadcaster import Broadcaster, Subscriber

HEARTBEAT_SECONDS = 15
RECONNECT_DELAY_MILLISECONDS = 3000


async def call_events(broadcaster: Broadcaster, account_id: int, request: Request) -> AsyncIterator[str]:
    subscriber = broadcaster.subscribe(account_id)
    try:
        yield f"retry: {RECONNECT_DELAY_MILLISECONDS}\n\n"
        while not subscriber.fell_behind and not await request.is_disconnected():
            yield await next_event(subscriber)
    finally:
        broadcaster.unsubscribe(account_id, subscriber)


async def next_event(subscriber: Subscriber) -> str:
    try:
        payload = await asyncio.wait_for(subscriber.queue.get(), timeout=HEARTBEAT_SECONDS)
    except TimeoutError:
        return ": heartbeat\n\n"
    return f"event: call\ndata: {payload}\n\n"
