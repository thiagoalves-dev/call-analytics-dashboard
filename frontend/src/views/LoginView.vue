<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
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
      <h1>Call Analytics</h1>
      <label>
        <span>Email</span>
        <input v-model="email" type="email" autocomplete="username" required />
      </label>
      <label>
        <span>Password</span>
        <input v-model="password" type="password" autocomplete="current-password" required />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="submitting">{{ submitting ? "Signing in…" : "Sign in" }}</button>
      <div class="demo">
        <span>Demo accounts</span>
        <button v-for="account in DEMO_ACCOUNTS" :key="account.email" type="button" @click="useDemoAccount(account)">
          {{ account.company }}
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
  padding: 16px;
}
form {
  width: 100%;
  max-width: 360px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
h1 {
  margin: 0 0 6px;
  font-size: 22px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--muted);
}
input {
  font: inherit;
  color: var(--text);
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 10px;
}
button[type="submit"] {
  font: inherit;
  font-weight: 600;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 10px;
  cursor: pointer;
}
.error {
  color: #e5484d;
  margin: 0;
  font-size: 14px;
}
.demo {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
  font-size: 13px;
  color: var(--muted);
  border-top: 1px solid var(--border);
  padding-top: 12px;
}
.demo button {
  font: inherit;
  background: var(--background);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 10px;
  cursor: pointer;
}
</style>
