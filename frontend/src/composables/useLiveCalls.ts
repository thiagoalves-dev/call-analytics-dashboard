import { onBeforeUnmount, onMounted, ref } from "vue";
import { CALL_STREAM_URL } from "../api/endpoints";
import type { Call } from "../api/types";
import { LiveCallStream, type StreamState } from "../lib/liveCallStream";

export type { StreamState } from "../lib/liveCallStream";

export function useLiveCalls(onCall: (call: Call) => void, onReconnect: () => void) {
  const streamState = ref<StreamState>("connecting");
  const onStateChange = (state: StreamState) => (streamState.value = state);
  const stream = new LiveCallStream(CALL_STREAM_URL, { onCall, onReconnect, onStateChange });
  const stop = () => stream.close();
  onMounted(() => stream.connect());
  onBeforeUnmount(stop);
  return { streamState, stop };
}
