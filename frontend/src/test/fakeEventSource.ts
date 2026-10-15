import type { Call } from "../api/types";

type Listener = (event: Event) => void;

export class FakeEventSource {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSED = 2;
  static instances: FakeEventSource[] = [];

  readyState = FakeEventSource.CONNECTING;
  private readonly listeners = new Map<string, Listener[]>();

  constructor(public readonly url: string) {
    FakeEventSource.instances.push(this);
  }

  static latest(): FakeEventSource {
    return FakeEventSource.instances[FakeEventSource.instances.length - 1];
  }

  addEventListener(type: string, listener: Listener): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  close(): void {
    this.readyState = FakeEventSource.CLOSED;
  }

  open(): void {
    this.readyState = FakeEventSource.OPEN;
    this.emit(new Event("open"));
  }

  failWithHttpError(): void {
    this.readyState = FakeEventSource.CLOSED;
    this.emit(new Event("error"));
  }

  dropNetwork(): void {
    this.readyState = FakeEventSource.CONNECTING;
    this.emit(new Event("error"));
  }

  sendCall(call: Call): void {
    this.emit(new MessageEvent("call", { data: JSON.stringify(call) }));
  }

  private emit(event: Event): void {
    this.listeners.get(event.type)?.forEach((listener) => listener(event));
  }
}
