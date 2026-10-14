export type CallStatus = "missed" | "connected" | "converted";
export type Granularity = "hour" | "day";
export type ConversionGrouping = "campaign" | "source";

export interface User {
  id: number;
  email: string;
  name: string;
  account_id: number;
  account_name: string;
  timezone: string;
}

export interface Campaign {
  id: number;
  name: string;
  source: string;
  tracking_number: string;
}

export interface Call {
  id: number;
  external_id: string | null;
  campaign_id: number;
  campaign_name: string;
  source: string;
  caller_number: string;
  started_at: string;
  duration_seconds: number;
  ended_at: string;
  status: CallStatus;
}

export interface VolumePoint {
  bucket: string;
  total: number;
  missed: number;
  connected: number;
  converted: number;
}

export interface VolumeResponse {
  granularity: Granularity;
  timezone: string;
  points: VolumePoint[];
}

export interface ConversionRow {
  key: string;
  label: string;
  source: string;
  calls: number;
  missed: number;
  connected: number;
  converted: number;
  conversion_rate: number | null;
}

export interface ConversionResponse {
  group_by: ConversionGrouping;
  rows: ConversionRow[];
}
