import { describe, expect, it } from "vitest";
import { formatBucket, formatCallTime, formatDuration, formatPhone, initialsOf } from "./format";

const NOW = new Date("2026-10-14T20:00:00Z");

describe("formatCallTime", () => {
  it("shows only the time for a call that ended today", () => {
    expect(formatCallTime("2026-10-14T19:26:14Z", "America/Chicago", NOW)).toBe("2:26:14 PM");
  });

  it("adds the date for a call that ended on an earlier day", () => {
    expect(formatCallTime("2026-10-13T19:26:14Z", "America/Chicago", NOW)).toBe("Oct 13, 2:26:14 PM");
  });
});

describe("formatBucket", () => {
  it("labels a daily bucket with the calendar day in the account timezone", () => {
    expect(formatBucket("2026-10-13T05:00:00Z", "day", "America/Chicago")).toBe("Tue, Oct 13");
  });

  it("does not shift a daily bucket into the previous UTC day", () => {
    expect(formatBucket("2026-10-14T04:00:00Z", "day", "America/New_York")).toBe("Wed, Oct 14");
  });

  it("labels an hourly bucket with the hour in the account timezone", () => {
    expect(formatBucket("2026-10-13T15:00:00Z", "hour", "America/Chicago")).toBe("Oct 13, 10 AM");
  });
});

describe("formatDuration", () => {
  it("pads the seconds to two digits", () => {
    expect(formatDuration(65)).toBe("1:05");
  });

  it("shows calls under a minute as zero minutes", () => {
    expect(formatDuration(9)).toBe("0:09");
  });
});

describe("formatPhone", () => {
  it("formats a US number with its country code", () => {
    expect(formatPhone("+15551234567")).toBe("(555) 123-4567");
  });

  it("leaves a number that isn't ten digits untouched", () => {
    expect(formatPhone("+442071234567")).toBe("+442071234567");
  });
});

describe("initialsOf", () => {
  it("takes the first letter of the first two words", () => {
    expect(initialsOf("Dana Brooks")).toBe("DB");
  });
});
