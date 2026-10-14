import type { Call, CallStatus, Granularity } from "../api/types";

export type RangePreset = "24h" | "7d" | "30d" | "90d" | "custom";

export interface Filters {
  preset: RangePreset;
  customStart: string;
  customEnd: string;
  campaignIds: number[];
  statuses: CallStatus[];
}

export interface DateRange {
  start: Date;
  end: Date;
}

const HOUR_IN_MS = 60 * 60 * 1000;
const DAY_IN_MS = 24 * HOUR_IN_MS;
const MAX_HOURLY_RANGE_IN_MS = 31 * DAY_IN_MS;

export const PRESET_DURATIONS_IN_MS: Record<Exclude<RangePreset, "custom">, number> = {
  "24h": DAY_IN_MS,
  "7d": 7 * DAY_IN_MS,
  "30d": 30 * DAY_IN_MS,
  "90d": 90 * DAY_IN_MS,
};

export const ALL_STATUSES: CallStatus[] = ["missed", "connected", "converted"];

export function defaultFilters(): Filters {
  return { preset: "7d", customStart: "", customEnd: "", campaignIds: [], statuses: [] };
}

export function isLive(filters: Filters): boolean {
  return filters.preset !== "custom";
}

export function rangeFor(filters: Filters, now: Date): DateRange {
  if (filters.preset === "custom") {
    return customRange(filters, now);
  }
  return { start: new Date(now.getTime() - PRESET_DURATIONS_IN_MS[filters.preset]), end: now };
}

function customRange(filters: Filters, now: Date): DateRange {
  const start = filters.customStart ? new Date(`${filters.customStart}T00:00:00`) : new Date(now.getTime() - DAY_IN_MS);
  const end = filters.customEnd ? new Date(new Date(`${filters.customEnd}T00:00:00`).getTime() + DAY_IN_MS) : now;
  return { start, end };
}

export function hourlyViewAllowed(range: DateRange): boolean {
  return range.end.getTime() - range.start.getTime() <= MAX_HOURLY_RANGE_IN_MS;
}

export function effectiveGranularity(requested: Granularity, range: DateRange): Granularity {
  return requested === "hour" && !hourlyViewAllowed(range) ? "day" : requested;
}

export function toQueryParams(filters: Filters, range: DateRange): URLSearchParams {
  const params = new URLSearchParams({ from: range.start.toISOString(), to: range.end.toISOString() });
  filters.campaignIds.forEach((campaignId) => params.append("campaign_id", String(campaignId)));
  filters.statuses.forEach((status) => params.append("status", status));
  return params;
}

export function callMatchesFilters(call: Call, filters: Filters): boolean {
  const campaignMatches = filters.campaignIds.length === 0 || filters.campaignIds.includes(call.campaign_id);
  const statusMatches = filters.statuses.length === 0 || filters.statuses.includes(call.status);
  return campaignMatches && statusMatches;
}
