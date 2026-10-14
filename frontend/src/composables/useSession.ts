import { ref } from "vue";
import { UnauthenticatedError } from "../api/client";
import { fetchCurrentUser, login, logout } from "../api/endpoints";
import type { User } from "../api/types";

const currentUser = ref<User | null>(null);

export function useSession() {
  async function restore(): Promise<User | null> {
    try {
      currentUser.value = await fetchCurrentUser();
    } catch (error) {
      if (!(error instanceof UnauthenticatedError)) throw error;
      currentUser.value = null;
    }
    return currentUser.value;
  }

  async function signIn(email: string, password: string): Promise<void> {
    currentUser.value = await login(email, password);
  }

  async function signOut(): Promise<void> {
    await logout();
    currentUser.value = null;
  }

  return { currentUser, restore, signIn, signOut };
}
