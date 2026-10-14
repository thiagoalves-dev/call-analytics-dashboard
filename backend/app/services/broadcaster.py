import asyncio
import contextlib
import logging
from collections import defaultdict

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

CHANNEL_PREFIX = "calls:"
SUBSCRIBER_QUEUE_SIZE = 100
RECONNECT_DELAY_SECONDS = 1


def channel_for(account_id: int) -> str:
    return f"{CHANNEL_PREFIX}{account_id}"


class Subscriber:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[str] = asyncio.Queue(maxsize=SUBSCRIBER_QUEUE_SIZE)
        self.fell_behind = False

    def deliver(self, payload: str) -> None:
        try:
            self.queue.put_nowait(payload)
        except asyncio.QueueFull:
            self.fell_behind = True


class Broadcaster:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.subscribers: dict[int, set[Subscriber]] = defaultdict(set)
        self.listener: asyncio.Task | None = None

    async def start(self) -> None:
        self.listener = asyncio.create_task(self.listen_forever())

    async def stop(self) -> None:
        if self.listener:
            self.listener.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.listener

    async def publish(self, account_id: int, payload: str) -> None:
        await self.redis.publish(channel_for(account_id), payload)

    def subscribe(self, account_id: int) -> Subscriber:
        subscriber = Subscriber()
        self.subscribers[account_id].add(subscriber)
        return subscriber

    def unsubscribe(self, account_id: int, subscriber: Subscriber) -> None:
        self.subscribers[account_id].discard(subscriber)
        if not self.subscribers[account_id]:
            del self.subscribers[account_id]

    async def listen_forever(self) -> None:
        while True:
            try:
                await self.listen()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Redis subscription lost, reconnecting")
                await asyncio.sleep(RECONNECT_DELAY_SECONDS)

    async def listen(self) -> None:
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe(f"{CHANNEL_PREFIX}*")
        async for message in pubsub.listen():
            if message["type"] == "pmessage":
                self.dispatch(message["channel"].decode(), message["data"].decode())

    def dispatch(self, channel: str, payload: str) -> None:
        account_id = int(channel.removeprefix(CHANNEL_PREFIX))
        for subscriber in list(self.subscribers.get(account_id, ())):
            subscriber.deliver(payload)
