import asyncio
import contextlib
import logging
from collections import defaultdict

from redis.asyncio import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

DEFAULT_CHANNEL_PREFIX = "calls:"
SUBSCRIBER_QUEUE_SIZE = 100
RECONNECT_DELAY_SECONDS = 1


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
    def __init__(self, redis: Redis, channel_prefix: str = DEFAULT_CHANNEL_PREFIX) -> None:
        self.redis = redis
        self.channel_prefix = channel_prefix
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
        try:
            await self.redis.publish(self.channel_for(account_id), payload)
        except RedisError:
            logger.exception("Could not publish to the live feed of account %s", account_id)

    def channel_for(self, account_id: int) -> str:
        return f"{self.channel_prefix}{account_id}"

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
        try:
            await pubsub.psubscribe(f"{self.channel_prefix}*")
            self.mark_all_subscribers_behind()
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    self.dispatch(message["channel"].decode(), message["data"].decode())
        finally:
            await pubsub.aclose()

    def mark_all_subscribers_behind(self) -> None:
        for subscribers in self.subscribers.values():
            for subscriber in subscribers:
                subscriber.fell_behind = True

    def dispatch(self, channel: str, payload: str) -> None:
        account_id = int(channel.removeprefix(self.channel_prefix))
        for subscriber in list(self.subscribers.get(account_id, ())):
            subscriber.deliver(payload)
