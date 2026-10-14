import { describe, expect, it } from "vitest";
import type { Call } from "../api/types";
import { callMatchesFilters, defaultFilters, effectiveGranularity, rangeFor, toQueryParams } from "./filters";

const NOW = new Date("2026-10-13T15:00:00Z");

const call = (overrides: Partial<Call> = {}): Call => ({
  id: 1,
  external_id: "provider-1",
  campaign_id: 1,
  campaign_name: "Google",
  source: "Google Ads",
  caller_number: "+15551234567",
  started_at: "2026-10-13T14:59:00Z",
  duration_seconds: 60,
  ended_at: "2026-10-13T15:00:00Z",
  status: "connected",
  ...overrides,
});

describe("rangeFor", () => {
  it("ends a preset range now", () => {
    const range = rangeFor({ ...defaultFilters(), preset: "24h" }, NOW);

    expect(range).toEqual({ start: new Date("2026-10-12T15:00:00Z"), end: NOW });
  });
});

describe("effectiveGranularity", () => {
  it("keeps the hourly view for ranges up to 31 days", () => {
    expect(effectiveGranularity("hour", rangeFor({ ...defaultFilters(), preset: "30d" }, NOW))).toBe("hour");
  });

  it("falls back to the daily view for longer ranges", () => {
    expect(effectiveGranularity("hour", rangeFor({ ...defaultFilters(), preset: "90d" }, NOW))).toBe("day");
  });
});

describe("toQueryParams", () => {
  it("repeats campaign and status parameters", () => {
    const filters = { ...defaultFilters(), campaignIds: [1, 2], statuses: ["missed" as const] };

    const params = toQueryParams(filters, rangeFor(filters, NOW));

    expect(params.getAll("campaign_id")).toEqual(["1", "2"]);
    expect(params.getAll("status")).toEqual(["missed"]);
    expect(params.get("to")).toBe("2026-10-13T15:00:00.000Z");
  });
});

describe("callMatchesFilters", () => {
  it("matches everything when nothing is selected", () => {
    expect(callMatchesFilters(call(), defaultFilters())).toBe(true);
  });

  it("rejects a live call from an unselected campaign", () => {
    expect(callMatchesFilters(call({ campaign_id: 3 }), { ...defaultFilters(), campaignIds: [1] })).toBe(false);
  });

  it("rejects a live call with an unselected outcome", () => {
    expect(callMatchesFilters(call({ status: "missed" }), { ...defaultFilters(), statuses: ["converted"] })).toBe(false);
  });
});
