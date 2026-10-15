import { onBeforeUnmount } from "vue";

export function useInterval(callback: () => void, intervalMs: number): void {
  const timer = setInterval(callback, intervalMs);
  onBeforeUnmount(() => clearInterval(timer));
}
