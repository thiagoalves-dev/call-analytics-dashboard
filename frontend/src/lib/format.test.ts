import { describe, expect, it } from "vitest";
import { formatCallTime, initialsOf } from "./format";

const NOW = new Date("2026-10-14T20:00:00Z");

describe("formatCallTime", () => {
  it("shows only the time for a call that ended today", () => {
    expect(formatCallTime("2026-10-14T19:26:14Z", "America/Chicago", NOW)).toBe("2:26:14 PM");
  });

  it("adds the date for a call that ended on an earlier day", () => {
    expect(formatCallTime("2026-10-13T19:26:14Z", "America/Chicago", NOW)).toBe("Oct 13, 2:26:14 PM");
  });
});

describe("initialsOf", () => {
  it("takes the first letter of the first two words", () => {
    expect(initialsOf("Dana Brooks")).toBe("DB");
  });
});
