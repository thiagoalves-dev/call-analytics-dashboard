import { describe, expect, it } from "vitest";
import { buildCall } from "../test/fixtures";
import { FEED_SIZE, mergeNewest } from "./feed";

const endingAt = (id: number, minute: number) =>
  buildCall({ id, ended_at: `2026-10-13T15:${String(minute).padStart(2, "0")}:00Z` });

describe("mergeNewest", () => {
  it("keeps one entry per call id, preferring the incoming version", () => {
    const converted = buildCall({ id: 1, status: "converted" });

    const merged = mergeNewest([converted], [buildCall({ id: 1, status: "connected" })]);

    expect(merged).toEqual([converted]);
  });

  it("orders calls by when they ended, newest first", () => {
    const merged = mergeNewest([endingAt(2, 5)], [endingAt(1, 10), endingAt(3, 1)]);

    expect(merged.map((call) => call.id)).toEqual([1, 2, 3]);
  });

  it("caps the feed at its size, dropping the oldest calls", () => {
    const current = Array.from({ length: FEED_SIZE }, (_, index) => endingAt(index + 1, index));

    const merged = mergeNewest([endingAt(999, 59)], current);

    expect(merged).toHaveLength(FEED_SIZE);
    expect(merged[0].id).toBe(999);
    expect(merged.map((call) => call.id)).not.toContain(1);
  });
});
