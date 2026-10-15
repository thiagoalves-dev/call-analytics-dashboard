import { ref } from "vue";
import { UnauthenticatedError } from "../api/client";

export function useLoadStatus(onUnauthenticated: () => void) {
  const error = ref<string | null>(null);
  const clearError = () => (error.value = null);
  function reportFailure(failure: unknown) {
    if (failure instanceof UnauthenticatedError) return onUnauthenticated();
    error.value = failure instanceof Error ? failure.message : String(failure);
  }
  function reportUnauthenticated(failure: unknown) {
    if (failure instanceof UnauthenticatedError) onUnauthenticated();
  }
  return { error, clearError, reportFailure, reportUnauthenticated };
}
