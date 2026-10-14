import { onBeforeUnmount, onMounted, ref } from "vue";
import { CALL_STREAM_URL } from "../api/endpoints";
import type { Call } from "../api/types";

export type StreamState = "connecting" | "live" | "reconnecting";

export function useLiveCalls(onCall: (call: Call) => void, onReconnect: () => void) {
  const streamState = ref<StreamState>("connecting");
  let source: EventSource | null = null;
  let hasConnectedBefore = false;

  function handleOpen() {
    streamState.value = "live";
    if (hasConnectedBefore) onReconnect();
    hasConnectedBefore = true;
  }

  function connect() {
    source = new EventSource(CALL_STREAM_URL);
    source.addEventListener("open", handleOpen);
    source.addEventListener("error", () => (streamState.value = "reconnecting"));
    source.addEventListener("call", (event) => onCall(JSON.parse((event as MessageEvent).data)));
  }

  onMounted(connect);
  onBeforeUnmount(() => source?.close());

  return { streamState };
}
