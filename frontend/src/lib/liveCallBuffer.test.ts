import { describe, expect, it } from "vitest";
import { buildCall } from "../test/fixtures";
import { LiveCallBuffer } from "./liveCallBuffer";

const older = buildCall({ id: 1, ended_at: "2026-10-13T15:00:00Z" });
const live = buildCall({ id: 2, ended_at: "2026-10-13T15:05:00Z" });

describe("LiveCallBuffer", () => {
  it("merges held calls into the feed once and then empties", () => {
    const buffer = new LiveCallBuffer();
    buffer.hold(live);

    const feed = buffer.mergeInto([older]);

    expect(feed).toEqual([live, older]);
    expect(buffer.mergeInto([older])).toEqual([older]);
  });

  it("keeps calls already shown when a feed response that predates them arrives", () => {
    const buffer = new LiveCallBuffer();
    buffer.startFeedRequest();
    buffer.hold(live);
    buffer.mergeInto([]);

    expect(buffer.mergeIntoFeedResponse([older])).toEqual([live, older]);
  });

  it("drops held calls when a new feed request starts", () => {
    const buffer = new LiveCallBuffer();
    buffer.hold(live);

    buffer.startFeedRequest();

    expect(buffer.mergeInto([older])).toEqual([older]);
  });
});
