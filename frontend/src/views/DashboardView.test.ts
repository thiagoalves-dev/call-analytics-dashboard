import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { defineComponent, h } from "vue";
import { createMemoryHistory, createRouter, RouterView } from "vue-router";
import { ApiError, UnauthenticatedError } from "../api/client";
import {
  fetchCampaigns,
  fetchConversion,
  fetchCurrentUser,
  fetchRecentCalls,
  fetchVolume,
} from "../api/endpoints";
import { LIVE_REFRESH_MS } from "../composables/useLiveMerge";
import { useSession } from "../composables/useSession";
import { sessionGuard } from "../sessionGuard";
import { FakeEventSource } from "../test/fakeEventSource";
import { USER, buildConversion, buildVolume } from "../test/fixtures";
import DashboardView from "./DashboardView.vue";

vi.mock("../api/endpoints", () => ({
  CALL_STREAM_URL: "/api/calls/stream",
  fetchCampaigns: vi.fn(),
  fetchConversion: vi.fn(),
  fetchCurrentUser: vi.fn(),
  fetchRecentCalls: vi.fn(),
  fetchVolume: vi.fn(),
  logout: vi.fn(),
}));

const LoginPage = defineComponent({ render: () => h("p", "login") });

async function openDashboard() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: DashboardView, meta: { requiresAuth: true } },
      { path: "/login", component: LoginPage },
    ],
  });
  router.beforeEach(sessionGuard);
  await router.push("/");
  const stubs = { VolumeChart: true, ConversionChart: true };
  const wrapper = mount(defineComponent({ render: () => h(RouterView) }), { global: { plugins: [router], stubs } });
  await flushPromises();
  return { router, wrapper };
}

function rejectEveryDataRequest(failure: Error) {
  [fetchCampaigns, fetchVolume, fetchConversion, fetchRecentCalls].forEach((fetcher) =>
    vi.mocked(fetcher).mockRejectedValue(failure),
  );
}

describe("DashboardView", () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    FakeEventSource.instances = [];
    vi.stubGlobal("EventSource", FakeEventSource);
    vi.mocked(fetchCurrentUser).mockResolvedValue(USER);
    vi.mocked(fetchCampaigns).mockResolvedValue([]);
    vi.mocked(fetchVolume).mockResolvedValue(buildVolume());
    vi.mocked(fetchConversion).mockResolvedValue(buildConversion([]));
    vi.mocked(fetchRecentCalls).mockResolvedValue([]);
  });

  afterEach(() => {
    useSession().endSession();
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.resetAllMocks();
  });

  it("returns to the login page when the session expires mid-session", async () => {
    const { router } = await openDashboard();
    rejectEveryDataRequest(new UnauthenticatedError("Not authenticated"));
    vi.mocked(fetchCurrentUser).mockRejectedValue(new UnauthenticatedError("Not authenticated"));

    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS);
    await flushPromises();

    expect(router.currentRoute.value.path).toBe("/login");
    expect(useSession().currentUser.value).toBeNull();
    expect(FakeEventSource.latest().readyState).toBe(FakeEventSource.CLOSED);
  });

  it("stops the refresh tick once the session has expired", async () => {
    await openDashboard();
    rejectEveryDataRequest(new UnauthenticatedError("Not authenticated"));
    vi.mocked(fetchCurrentUser).mockRejectedValue(new UnauthenticatedError("Not authenticated"));
    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS);
    vi.mocked(fetchVolume).mockClear();

    await vi.advanceTimersByTimeAsync(LIVE_REFRESH_MS * 2);

    expect(fetchVolume).not.toHaveBeenCalled();
  });

  it("shows the dashboard with a visible error when campaigns fail to load", async () => {
    vi.mocked(fetchCampaigns).mockRejectedValue(new ApiError("Campaigns are unavailable", 500));

    const { wrapper } = await openDashboard();

    expect(wrapper.get("[role=alert]").text()).toBe("Campaigns are unavailable");
    expect(fetchVolume).toHaveBeenCalled();
  });

  it("marks the selected volume granularity as pressed", async () => {
    const { wrapper } = await openDashboard();

    const pressed = wrapper.findAll("[aria-pressed=true]").map((button) => button.text());

    expect(pressed).toEqual(expect.arrayContaining(["Hourly", "By campaign"]));
  });
});
