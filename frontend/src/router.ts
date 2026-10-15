import { createRouter, createWebHistory } from "vue-router";
import { UNAVAILABLE_PATH, sessionGuard } from "./sessionGuard";
import DashboardView from "./views/DashboardView.vue";
import LoginView from "./views/LoginView.vue";
import UnavailableView from "./views/UnavailableView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: DashboardView, meta: { requiresAuth: true } },
    { path: "/login", component: LoginView },
    { path: UNAVAILABLE_PATH, component: UnavailableView },
  ],
});

router.beforeEach(sessionGuard);
