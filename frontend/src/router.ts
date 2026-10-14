import { createRouter, createWebHistory } from "vue-router";
import { useSession } from "./composables/useSession";
import DashboardView from "./views/DashboardView.vue";
import LoginView from "./views/LoginView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardView, meta: { requiresAuth: true } },
    { path: "/login", component: LoginView },
  ],
});

router.beforeEach(async (to) => {
  const { currentUser, restore } = useSession();
  const user = currentUser.value ?? (await restore());
  if (to.meta.requiresAuth && !user) return "/login";
  if (to.path === "/login" && user) return "/";
});
