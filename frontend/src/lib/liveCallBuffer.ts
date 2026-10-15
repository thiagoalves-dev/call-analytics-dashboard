import type { Call } from "../api/types";
import { mergeNewest } from "./feed";

export class LiveCallBuffer {
  private held: Call[] = [];
  private shownSinceFeedRequest: Call[] = [];

  hold(call: Call): void {
    this.held.push(call);
  }

  mergeInto(feed: Call[]): Call[] {
    const merged = mergeNewest(this.held, feed);
    this.shownSinceFeedRequest.push(...this.held);
    this.held = [];
    return merged;
  }

  startFeedRequest(): void {
    this.held = [];
    this.shownSinceFeedRequest = [];
  }

  mergeIntoFeedResponse(response: Call[]): Call[] {
    return mergeNewest(this.shownSinceFeedRequest, response);
  }
}
