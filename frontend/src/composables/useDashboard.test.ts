import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { defineComponent, nextTick } from "vue";
import { ApiError, UnauthenticatedError } from "../api/client";
import { fetchCampaigns, fetchConversion, fetchRecentCalls, fetchVolume } from "../api/endpoints";
import type { Call, ConversionResponse } from "../api/types";
import { buildCall, buildConversion, buildConversionRow, buildVolume, deferred } from "../test/fixtures";
import { useDashboard } from "./useDashboard";
import { LIVE_REFRESH_MS } from "./useLiveMerge";

vi.mock("../api/endpoints", () => ({
  fetchCampaigns: vi.fn(),
  fetchConversion: vi.fn(),
  fetchRecentCalls: vi.fn(),
  fetchVolume: vi.fn(),
}));

const LAST_90_DAYS = buildConversion([buildConversionRow({ calls: 9000 })]);
const LAST_24_HOURS = buildConversion([buildConversionRow({ calls: 100 })]);
const FEED_CALL = buildCall({ id: 1, ended_at: "2026-10-13T15:00:00Z" });
const LIVE_CALL = buildCall({ id: 2, ended_at: "2026-10-13T15:05:00Z" });

function mountDashboard(onUnauthenticated = vi.fn()) {
  let dashboard!: ReturnType<typeof useDashboard>;
  const Host = defineComponent({
    setup() {
      dashboard = useDashboard(onUnauthenticated);
      return () => null;
    },
  });
  const wrapper = mount(Host);
  return { dashboard, wrapper, onUnauthenticated };
}

async function settle() {
  await nextTick();
  await flushPromises();
}

describe("useDashboard", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.mocked(fetchCampaigns).mockResolvedValue([]);
    vi.mocked(fetchVolume).mockResolvedValue(buildVolume());
    vi.mocked(fetchConversion).mockResolvedValue(LAST_24_HOURS);
    vi.mocked(fetchRecentCalls).mockResolvedValue([]);
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.resetAllMocks();
  });

  it("ignores a slow response for a range the user already left", async () => {
    const slowNinetyDays = deferred<ConversionResponse>();
    vi.mocked(fetchConversion).mockReturnValueOnce(slowNinetyDays.promise).mockResolvedValueOnce(LAST_24_HOURS);
    const { dashboard } = mountDashboard();

    dashboard.filters.preset = "90d";
    await settle();
    dashboard.filters.preset = "24h";
    await settle();
    slowNinetyDays.resolve(LAST_90_DAYS);
    await settle();

    expect(dashboard.conversion.value).toEqual(LAST_24_HOURS);
  });

  it("ignores a live chart refresh that lands after a filter change", async () => {
    const slowLiveRefresh = deferred<ConversionResponse>();
    vi.mocked(fetchConversion).mockReturnValueOnce(slowLiveRefresh.promise).mockResolvedValueOnce(LAST_24_HOURS);
    const { dashboard } = mountDashboard();

    dashboard.receiveLiveCall(LIVE_CALL);
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS);
    dashboard.filters.preset = "24h";
    await settle();
    slowLiveRefresh.resolve(LAST_90_DAYS);
    await settle();

    expect(dashboard.conversion.value).toEqual(LAST_24_HOURS);
  });

  it("keeps live calls already merged when an older feed request finishes", async () => {
    const slowFeed = deferred<Call[]>();
    vi.mocked(fetchRecentCalls).mockReturnValueOnce(slowFeed.promise);
    const { dashboard } = mountDashboard();

    void dashboard.reload();
    dashboard.receiveLiveCall(LIVE_CALL);
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS);
    expect(dashboard.feed.value).toEqual([LIVE_CALL]);
    slowFeed.resolve([FEED_CALL]);
    await settle();

    expect(dashboard.feed.value).toEqual([LIVE_CALL, FEED_CALL]);
  });

  it("shows held live calls only on the next refresh tick", async () => {
    const { dashboard } = mountDashboard();
    await dashboard.reload();

    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS / 4);
    dashboard.receiveLiveCall(FEED_CALL);
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS / 4);
    dashboard.receiveLiveCall(LIVE_CALL);
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS / 2 - 1);
    expect(dashboard.feed.value).toEqual([]);
    await vi.advanceTimersByTimeAsync(1);

    expect(dashboard.feed.value).toEqual([LIVE_CALL, FEED_CALL]);
  });

  it("refetches the charts on every refresh tick even without live calls", async () => {
    const ticks = 3;
    mountDashboard();

    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS * ticks);

    expect(fetchVolume).toHaveBeenCalledTimes(ticks);
    expect(fetchConversion).toHaveBeenCalledTimes(ticks);
    expect(fetchRecentCalls).not.toHaveBeenCalled();
  });

  it("drops live calls that don't match the filters", async () => {
    const { dashboard } = mountDashboard();
    dashboard.filters.statuses = ["converted"];
    await settle();

    dashboard.receiveLiveCall(buildCall({ status: "missed" }));
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS);

    expect(dashboard.feed.value).toEqual([]);
  });

  it("hands an expired session to the caller instead of showing an error", async () => {
    vi.mocked(fetchVolume).mockRejectedValue(new UnauthenticatedError("Not authenticated"));
    const { dashboard, onUnauthenticated } = mountDashboard();

    await dashboard.reload();

    expect(onUnauthenticated).toHaveBeenCalled();
    expect(dashboard.error.value).toBeNull();
  });

  it("still loads the dashboard and shows the error when campaigns fail to load", async () => {
    vi.mocked(fetchCampaigns).mockRejectedValue(new ApiError("Campaigns are unavailable", 500));
    const { dashboard } = mountDashboard();

    await dashboard.start();

    expect(dashboard.error.value).toBe("Campaigns are unavailable");
    expect(dashboard.conversion.value).toEqual(LAST_24_HOURS);
  });

  it("stops its timers when unmounted", async () => {
    const { dashboard, wrapper } = mountDashboard();
    dashboard.receiveLiveCall(LIVE_CALL);

    wrapper.unmount();
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS * 3);

    expect(fetchVolume).not.toHaveBeenCalled();
  });
});
