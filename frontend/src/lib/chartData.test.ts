import { describe, expect, it } from "vitest";
import { buildConversionRow, buildVolume } from "../test/fixtures";
import {
  conversionChartData,
  conversionChartSummary,
  toRoundedPercent,
  volumeChartData,
  volumeChartSummary,
} from "./chartData";

describe("toRoundedPercent", () => {
  it("rounds a rate to one decimal place of a percent", () => {
    expect(toRoundedPercent(0.12345)).toBe(12.3);
    expect(toRoundedPercent(0.12355)).toBe(12.4);
  });

  it("treats a missing rate as zero percent", () => {
    expect(toRoundedPercent(null)).toBe(0);
  });
});

describe("conversionChartData", () => {
  it("maps rows to labels, percentages and call counts", () => {
    const rows = [buildConversionRow({ label: "Google", conversion_rate: 0.3, calls: 10 })];

    expect(conversionChartData(rows)).toEqual({ labels: ["Google"], ratesInPercent: [30], calls: [10] });
  });

  it("shows a row without calls as zero percent", () => {
    const rows = [buildConversionRow({ conversion_rate: null, calls: 0 })];

    expect(conversionChartData(rows).ratesInPercent).toEqual([0]);
  });
});

describe("chart summaries", () => {
  it("describes the volume totals per outcome", () => {
    const point = { bucket: "2026-10-13T15:00:00Z", total: 6, missed: 1, connected: 2, converted: 3 };

    const summary = volumeChartSummary(volumeChartData(buildVolume({ points: [point, point] })));

    expect(summary).toBe("Call volume across 2 periods: 2 missed, 4 connected, 6 converted.");
  });

  it("lists the conversion rate of every bar", () => {
    const data = conversionChartData([buildConversionRow({ label: "Google", conversion_rate: 0.3 })]);

    expect(conversionChartSummary(data)).toBe("Conversion rate: Google 30%.");
  });
});
