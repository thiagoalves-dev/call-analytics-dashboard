<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import LogoMark from "../components/LogoMark.vue";

const route = useRoute();
const router = useRouter();
const retrying = ref(false);
const destination = computed(() => (typeof route.query.next === "string" ? route.query.next : "/"));

async function retry() {
  retrying.value = true;
  try {
    await router.replace(destination.value);
  } finally {
    retrying.value = false;
  }
}
</script>

<template>
  <main class="unavailable">
    <section class="card" role="alert">
      <LogoMark :size="40" />
      <h1>Can't reach the server</h1>
      <p>The dashboard couldn't connect to the API. Check your connection and try again.</p>
      <button type="button" :disabled="retrying" @click="retry">{{ retrying ? "Retrying…" : "Retry" }}</button>
    </section>
  </main>
</template>

<style scoped>
.unavailable {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px 16px;
  background:
    radial-gradient(60% 50% at 50% 0%, var(--accent-soft), transparent 70%),
    var(--background);
}
.card {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow-raised);
  padding: 32px 28px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
}
h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
button {
  width: 100%;
  font-weight: 600;
  background: var(--accent);
  color: var(--on-accent);
  border: none;
  border-radius: 8px;
  padding: 10px;
  margin-top: 4px;
  cursor: pointer;
}
button:disabled {
  opacity: 0.7;
  cursor: progress;
}
</style>
