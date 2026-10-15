import type { Call, CallStatus, Granularity } from "../api/types";

export type RangePreset = "24h" | "7d" | "30d" | "90d";

export interface Filters {
  preset: RangePreset;
  campaignIds: number[];
  statuses: CallStatus[];
}

interface DateRange {
  start: Date;
  end: Date;
}

const HOUR_IN_MS = 60 * 60 * 1000;
const DAY_IN_MS = 24 * HOUR_IN_MS;
export const MAX_HOURLY_RANGE_IN_DAYS = 31;
const MAX_HOURLY_RANGE_IN_MS = MAX_HOURLY_RANGE_IN_DAYS * DAY_IN_MS;

const PRESET_DURATIONS_IN_MS: Record<RangePreset, number> = {
  "24h": DAY_IN_MS,
  "7d": 7 * DAY_IN_MS,
  "30d": 30 * DAY_IN_MS,
  "90d": 90 * DAY_IN_MS,
};

export const ALL_STATUSES: CallStatus[] = ["missed", "connected", "converted"];

export function defaultFilters(): Filters {
  return { preset: "7d", campaignIds: [], statuses: [] };
}

export function rangeFor(filters: Filters, now: Date): DateRange {
  return { start: new Date(now.getTime() - PRESET_DURATIONS_IN_MS[filters.preset]), end: now };
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
