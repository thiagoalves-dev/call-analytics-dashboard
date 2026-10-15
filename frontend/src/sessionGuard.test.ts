import { flushPromises, mount } from "@vue/test-utils";
import { afterEach, describe, expect, it, vi } from "vitest";
import { defineComponent, h } from "vue";
import { createMemoryHistory, createRouter, RouterView, type RouteLocationNormalized } from "vue-router";
import { UnauthenticatedError } from "./api/client";
import { fetchCurrentUser } from "./api/endpoints";
import { useSession } from "./composables/useSession";
import { UNAVAILABLE_PATH, sessionGuard } from "./sessionGuard";
import { USER } from "./test/fixtures";
import UnavailableView from "./views/UnavailableView.vue";

vi.mock("./api/endpoints", () => ({ fetchCurrentUser: vi.fn() }));

const SERVER_DOWN = new TypeError("Failed to fetch");
const Page = defineComponent({ render: () => h("p", "page") });

const routeTo = (path: string, requiresAuth = false) =>
  ({ path, fullPath: path, meta: { requiresAuth } }) as unknown as RouteLocationNormalized;

function mountRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: "/", component: Page, meta: { requiresAuth: true } },
      { path: "/login", component: Page },
      { path: UNAVAILABLE_PATH, component: UnavailableView },
    ],
  });
  router.beforeEach(sessionGuard);
  const wrapper = mount(defineComponent({ render: () => h(RouterView) }), { global: { plugins: [router] } });
  return { router, wrapper };
}

describe("sessionGuard", () => {
  afterEach(() => {
    useSession().endSession();
    vi.resetAllMocks();
  });

  it("sends a visitor without a session to the login page", async () => {
    vi.mocked(fetchCurrentUser).mockRejectedValue(new UnauthenticatedError("Not authenticated"));

    expect(await sessionGuard(routeTo("/", true))).toBe("/login");
  });

  it("sends a signed-in user away from the login page", async () => {
    vi.mocked(fetchCurrentUser).mockResolvedValue(USER);

    expect(await sessionGuard(routeTo("/login"))).toBe("/");
  });

  it("lets a signed-in user open the dashboard", async () => {
    vi.mocked(fetchCurrentUser).mockResolvedValue(USER);

    expect(await sessionGuard(routeTo("/", true))).toBe(true);
  });

  it("shows the unavailable page when the server can't be reached", async () => {
    vi.mocked(fetchCurrentUser).mockRejectedValue(SERVER_DOWN);

    expect(await sessionGuard(routeTo("/", true))).toEqual({ path: UNAVAILABLE_PATH, query: { next: "/" } });
  });

  it("renders the unavailable page and retries the original route", async () => {
    vi.mocked(fetchCurrentUser).mockRejectedValueOnce(SERVER_DOWN).mockResolvedValue(USER);
    const { router, wrapper } = mountRouter();

    await router.push("/");
    await flushPromises();
    expect(router.currentRoute.value.path).toBe(UNAVAILABLE_PATH);
    expect(wrapper.get("[role=alert]").text()).toContain("Can't reach the server");
    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(router.currentRoute.value.path).toBe("/");
  });
});
