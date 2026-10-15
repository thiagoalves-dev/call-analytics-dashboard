import type { RouteLocationNormalized, RouteLocationRaw } from "vue-router";
import { useSession } from "./composables/useSession";

export const UNAVAILABLE_PATH = "/unavailable";

export async function sessionGuard(to: RouteLocationNormalized): Promise<RouteLocationRaw | true> {
  if (to.path === UNAVAILABLE_PATH) return true;
  const { currentUser, restore } = useSession();
  try {
    const user = currentUser.value ?? (await restore());
    if (to.meta.requiresAuth && !user) return "/login";
    if (to.path === "/login" && user) return "/";
    return true;
  } catch {
    return { path: UNAVAILABLE_PATH, query: { next: to.fullPath } };
  }
}
