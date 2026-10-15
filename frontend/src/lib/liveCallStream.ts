import type { Call } from "../api/types";

export type StreamState = "connecting" | "live" | "reconnecting";

export const RECONNECT_BASE_DELAY_MS = 1_000;
export const RECONNECT_MAX_DELAY_MS = 30_000;

export interface LiveCallStreamHandlers {
  onCall: (call: Call) => void;
  onReconnect: () => void;
  onStateChange: (state: StreamState) => void;
}

export class LiveCallStream {
  private source: EventSource | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private failedAttempts = 0;
  private interrupted = false;

  constructor(
    private readonly url: string,
    private readonly handlers: LiveCallStreamHandlers,
  ) {}

  connect(): void {
    this.reconnectTimer = null;
    this.source = new EventSource(this.url);
    this.source.addEventListener("open", () => this.handleOpen());
    this.source.addEventListener("error", () => this.handleError());
    this.source.addEventListener("call", (event) => this.handlers.onCall(JSON.parse((event as MessageEvent).data)));
  }

  close(): void {
    this.source?.close();
    this.source = null;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
  }

  private handleOpen(): void {
    this.handlers.onStateChange("live");
    this.failedAttempts = 0;
    if (this.interrupted) this.handlers.onReconnect();
    this.interrupted = false;
  }

  private handleError(): void {
    this.handlers.onStateChange("reconnecting");
    this.interrupted = true;
    if (this.source?.readyState === EventSource.CLOSED) this.reconnectAfterBackoff();
  }

  private reconnectAfterBackoff(): void {
    this.close();
    const delay = Math.min(RECONNECT_BASE_DELAY_MS * 2 ** this.failedAttempts, RECONNECT_MAX_DELAY_MS);
    this.failedAttempts += 1;
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }
}
