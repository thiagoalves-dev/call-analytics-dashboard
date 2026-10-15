import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      "/api": { target: "http://localhost:1012", changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
  },
});
