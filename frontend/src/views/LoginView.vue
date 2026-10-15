<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import LogoMark from "../components/LogoMark.vue";
import { useSession } from "../composables/useSession";

const DEMO_ACCOUNTS = [
  { company: "Acme Home Services", email: "manager@acme.test", password: "acme-demo" },
  { company: "Summit Auto Group", email: "manager@summit.test", password: "summit-demo" },
];

const router = useRouter();
const { signIn } = useSession();
const email = ref("");
const password = ref("");
const error = ref<string | null>(null);
const submitting = ref(false);

async function submit() {
  submitting.value = true;
  error.value = null;
  try {
    await signIn(email.value, password.value);
    await router.push("/");
  } catch (failure) {
    error.value = failure instanceof Error ? failure.message : "Login failed";
  } finally {
    submitting.value = false;
  }
}

function useDemoAccount(account: (typeof DEMO_ACCOUNTS)[number]) {
  email.value = account.email;
  password.value = account.password;
}
</script>

<template>
  <main class="login">
    <form @submit.prevent="submit">
      <div class="brand">
        <LogoMark :size="40" />
        <h1>Call Analytics</h1>
        <p>Sign in to see how your inbound calls perform.</p>
      </div>
      <label>
        <span>Email</span>
        <input v-model="email" type="email" autocomplete="username" placeholder="you@company.com" required />
      </label>
      <label>
        <span>Password</span>
        <input
          v-model="password"
          type="password"
          autocomplete="current-password"
          placeholder="••••••••"
          required
        />
      </label>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? "Signing in…" : "Sign in" }}</button>
      <div class="demo">
        <span class="demo-title">Demo accounts</span>
        <button
          v-for="account in DEMO_ACCOUNTS"
          :key="account.email"
          type="button"
          :class="{ selected: email === account.email }"
          @click="useDemoAccount(account)"
        >
          <span class="initial" aria-hidden="true">{{ account.company[0] }}</span>
          <span class="details">
            <strong>{{ account.company }}</strong>
            <small>{{ account.email }}</small>
          </span>
          <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6 3.5 10.5 8 6 12.5" /></svg>
        </button>
      </div>
    </form>
  </main>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px 16px;
  background:
    radial-gradient(60% 50% at 50% 0%, var(--accent-soft), transparent 70%),
    var(--background);
}
form {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow-raised);
  padding: 32px 28px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 4px;
  margin-bottom: 8px;
}
h1 {
  margin: 12px 0 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.brand p {
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text);
}
input {
  font: inherit;
  font-weight: 400;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 9px 12px;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
input::placeholder {
  color: var(--muted);
  opacity: 0.6;
}
input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}
button[type="submit"] {
  font-weight: 600;
  background: var(--accent);
  color: var(--on-accent);
  border: none;
  border-radius: 8px;
  padding: 10px;
  margin-top: 4px;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  transition: filter 0.15s ease;
}
button[type="submit"]:hover:not(:disabled) {
  filter: brightness(1.08);
}
button[type="submit"]:disabled {
  opacity: 0.7;
  cursor: progress;
}
.error {
  color: var(--missed-ink);
  background: var(--missed-soft);
  border-radius: 8px;
  padding: 8px 12px;
  margin: 0;
  font-size: 13px;
}
.demo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: 1px solid var(--border);
  padding-top: 18px;
  margin-top: 4px;
}
.demo-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.demo button {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  text-align: left;
  color: var(--text);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: border-color 0.15s ease, background-color 0.15s ease;
}
.demo button:hover {
  border-color: var(--border-strong);
  background: var(--subtle);
}
.demo button.selected {
  border-color: var(--accent);
  background: var(--accent-soft);
}
.initial {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-ink);
  background: var(--accent-soft);
}
.details {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}
.details strong {
  font-size: 13px;
  font-weight: 600;
}
.details small {
  font-size: 12px;
  color: var(--muted);
}
.demo svg {
  width: 14px;
  height: 14px;
  fill: none;
  stroke: var(--muted);
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}
</style>
