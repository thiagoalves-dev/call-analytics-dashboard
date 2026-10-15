import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { FakeEventSource } from "../test/fakeEventSource";
import { buildCall } from "../test/fixtures";
import { LiveCallStream, RECONNECT_BASE_DELAY_MS, RECONNECT_MAX_DELAY_MS, type StreamState } from "./liveCallStream";

function connectStream() {
  const handlers = { onCall: vi.fn(), onReconnect: vi.fn(), onStateChange: vi.fn<(state: StreamState) => void>() };
  const stream = new LiveCallStream("/api/calls/stream", handlers);
  stream.connect();
  return { stream, handlers };
}

describe("LiveCallStream", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    FakeEventSource.instances = [];
    vi.stubGlobal("EventSource", FakeEventSource);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("passes every call event to the handler", () => {
    const { handlers } = connectStream();

    FakeEventSource.latest().sendCall(buildCall({ id: 7 }));

    expect(handlers.onCall).toHaveBeenCalledWith(buildCall({ id: 7 }));
  });

  it("reconnects after a backoff when the server answers with an HTTP error", () => {
    connectStream();

    FakeEventSource.latest().failWithHttpError();
    vi.advanceTimersByTime(RECONNECT_BASE_DELAY_MS - 1);
    expect(FakeEventSource.instances).toHaveLength(1);
    vi.advanceTimersByTime(1);

    expect(FakeEventSource.instances).toHaveLength(2);
  });

  it("reloads the dashboard once the reconnected stream opens", () => {
    const { handlers } = connectStream();
    FakeEventSource.latest().open();

    FakeEventSource.latest().failWithHttpError();
    vi.advanceTimersByTime(RECONNECT_BASE_DELAY_MS);
    FakeEventSource.latest().open();

    expect(handlers.onReconnect).toHaveBeenCalledOnce();
    expect(handlers.onStateChange).toHaveBeenLastCalledWith("live");
  });

  it("doubles the backoff after each failed attempt, up to a maximum", () => {
    connectStream();
    const delays = [1, 2, 4, 8, 16, 30, 30].map((factor) =>
      Math.min(RECONNECT_BASE_DELAY_MS * factor, RECONNECT_MAX_DELAY_MS),
    );

    delays.forEach((delay, attempt) => {
      FakeEventSource.latest().failWithHttpError();
      vi.advanceTimersByTime(delay);
      expect(FakeEventSource.instances).toHaveLength(attempt + 2);
    });
  });

  it("leaves network drops to the browser's own retry", () => {
    const { handlers } = connectStream();

    FakeEventSource.latest().dropNetwork();
    vi.advanceTimersByTime(RECONNECT_MAX_DELAY_MS);

    expect(FakeEventSource.instances).toHaveLength(1);
    expect(handlers.onStateChange).toHaveBeenLastCalledWith("reconnecting");
  });

  it("cancels a pending reconnect when closed", () => {
    const { stream } = connectStream();

    FakeEventSource.latest().failWithHttpError();
    stream.close();
    vi.advanceTimersByTime(RECONNECT_MAX_DELAY_MS);

    expect(FakeEventSource.instances).toHaveLength(1);
  });
});
