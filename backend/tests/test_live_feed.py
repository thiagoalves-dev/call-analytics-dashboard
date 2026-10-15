import asyncio
from unittest.mock import AsyncMock, MagicMock

from redis.exceptions import ConnectionError as RedisConnectionError

from app.services import broadcaster as broadcaster_module
from app.services import live_feed
from app.services.broadcaster import SUBSCRIBER_QUEUE_SIZE, Broadcaster, Subscriber

ACCOUNT_ID = 1


class FakePubSub:
    def __init__(self, connection_works: bool) -> None:
        self.connection_works = connection_works
        self.subscribed = asyncio.Event()
        self.closed = False

    async def psubscribe(self, pattern: str) -> None:
        if not self.connection_works:
            raise RedisConnectionError("Connection lost")
        self.subscribed.set()

    async def listen(self):
        await asyncio.Event().wait()
        yield {}

    async def aclose(self) -> None:
        self.closed = True


def broadcaster_without_redis() -> Broadcaster:
    return Broadcaster(redis=AsyncMock())


async def test_dispatch_delivers_only_to_the_accounts_subscribers():
    broadcaster = broadcaster_without_redis()
    acme = broadcaster.subscribe(1)
    summit = broadcaster.subscribe(2)

    broadcaster.dispatch(broadcaster.channel_for(1), '{"id": 7}')

    assert acme.queue.get_nowait() == '{"id": 7}'
    assert summit.queue.empty()


async def test_a_subscriber_that_falls_behind_is_flagged_instead_of_growing_forever():
    subscriber = Subscriber()

    for event_number in range(SUBSCRIBER_QUEUE_SIZE + 1):
        subscriber.deliver(str(event_number))

    assert subscriber.fell_behind
    assert subscriber.queue.qsize() == SUBSCRIBER_QUEUE_SIZE


async def test_unsubscribing_the_last_subscriber_forgets_the_account():
    broadcaster = broadcaster_without_redis()
    subscriber = broadcaster.subscribe(1)

    broadcaster.unsubscribe(1, subscriber)

    assert broadcaster.subscribers == {}


async def test_next_event_formats_a_call_as_a_server_sent_event():
    subscriber = Subscriber()
    subscriber.deliver('{"id": 7}')

    assert await live_feed.next_event(subscriber) == 'event: call\ndata: {"id": 7}\n\n'


async def test_next_event_sends_a_heartbeat_when_nothing_happens(monkeypatch):
    monkeypatch.setattr(live_feed, "HEARTBEAT_SECONDS", 0.01)

    assert await live_feed.next_event(Subscriber()) == ": heartbeat\n\n"


async def test_the_stream_stops_and_unsubscribes_when_the_browser_disconnects():
    broadcaster = broadcaster_without_redis()
    request = AsyncMock()
    request.is_disconnected.return_value = True

    events = [event async for event in live_feed.call_events(broadcaster, 1, request)]

    assert events == ["retry: 3000\n\n"]
    assert broadcaster.subscribers == {}


async def test_the_stream_ends_when_the_subscriber_falls_behind():
    broadcaster = broadcaster_without_redis()
    request = AsyncMock()
    request.is_disconnected.return_value = False
    events = live_feed.call_events(broadcaster, ACCOUNT_ID, request)

    assert await anext(events) == "retry: 3000\n\n"
    broadcaster.mark_all_subscribers_behind()

    assert [event async for event in events] == []
    assert broadcaster.subscribers == {}


async def test_a_reconnect_closes_the_lost_subscription_and_flags_every_subscriber(monkeypatch):
    monkeypatch.setattr(broadcaster_module, "RECONNECT_DELAY_SECONDS", 0)
    lost, healthy = FakePubSub(connection_works=False), FakePubSub(connection_works=True)
    broadcaster = Broadcaster(redis=MagicMock(pubsub=MagicMock(side_effect=[lost, healthy])))
    subscriber = broadcaster.subscribe(ACCOUNT_ID)

    await broadcaster.start()
    await asyncio.wait_for(healthy.subscribed.wait(), timeout=2)
    await broadcaster.stop()

    assert lost.closed
    assert healthy.closed
    assert subscriber.fell_behind


async def test_published_calls_reach_subscribers_through_redis(broadcaster):
    subscriber = broadcaster.subscribe(42)
    try:
        await broadcaster.publish(42, "hello")
        assert await asyncio.wait_for(subscriber.queue.get(), timeout=2) == "hello"
    finally:
        broadcaster.unsubscribe(42, subscriber)
