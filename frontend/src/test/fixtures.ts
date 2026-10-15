import type { Call, ConversionResponse, ConversionRow, User, VolumeResponse } from "../api/types";

export const USER: User = {
  id: 1,
  email: "manager@acme.test",
  name: "Dana Brooks",
  account_id: 1,
  account_name: "Acme Home Services",
  timezone: "America/Chicago",
};

export const buildCall = (overrides: Partial<Call> = {}): Call => ({
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

export const buildConversionRow = (overrides: Partial<ConversionRow> = {}): ConversionRow => ({
  key: "1",
  label: "Google",
  source: "Google Ads",
  calls: 10,
  missed: 2,
  connected: 5,
  converted: 3,
  conversion_rate: 0.3,
  ...overrides,
});

export const buildConversion = (rows: ConversionRow[]): ConversionResponse => ({ group_by: "campaign", rows });

export const buildVolume = (overrides: Partial<VolumeResponse> = {}): VolumeResponse => ({
  granularity: "hour",
  timezone: "America/Chicago",
  points: [],
  ...overrides,
});

export function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: unknown) => void;
  const promise = new Promise<T>((onResolve, onReject) => {
    resolve = onResolve;
    reject = onReject;
  });
  return { promise, resolve, reject };
}
