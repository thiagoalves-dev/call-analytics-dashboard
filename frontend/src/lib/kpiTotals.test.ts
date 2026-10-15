import { describe, expect, it } from "vitest";
import { buildConversionRow } from "../test/fixtures";
import { shareOfCalls, sumConversionRows } from "./kpiTotals";

describe("sumConversionRows", () => {
  it("adds calls, missed and converted across every row", () => {
    const rows = [
      buildConversionRow({ calls: 10, missed: 2, converted: 3 }),
      buildConversionRow({ calls: 30, missed: 6, converted: 9 }),
    ];

    expect(sumConversionRows(rows)).toEqual({ calls: 40, missed: 8, converted: 12 });
  });

  it("returns zero totals without rows", () => {
    expect(sumConversionRows([])).toEqual({ calls: 0, missed: 0, converted: 0 });
  });
});

describe("shareOfCalls", () => {
  it("divides by the total number of calls", () => {
    expect(shareOfCalls(12, { calls: 40, missed: 8, converted: 12 })).toBe(0.3);
  });

  it("has no rate when there are no calls", () => {
    expect(shareOfCalls(0, { calls: 0, missed: 0, converted: 0 })).toBeNull();
  });
});
