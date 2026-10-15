import { request } from "./client";
import type {
  Call,
  Campaign,
  ConversionGrouping,
  ConversionResponse,
  Granularity,
  User,
  VolumeResponse,
} from "./types";

export const login = (email: string, password: string) =>
  request<User>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });

export const logout = () => request<void>("/api/auth/logout", { method: "POST" });

export const fetchCurrentUser = () => request<User>("/api/auth/me");

export const fetchCampaigns = () => request<Campaign[]>("/api/campaigns");

export const fetchVolume = (query: URLSearchParams, granularity: Granularity) =>
  request<VolumeResponse>(`/api/stats/volume?${withParam(query, "granularity", granularity)}`);

export const fetchConversion = (query: URLSearchParams, groupBy: ConversionGrouping) =>
  request<ConversionResponse>(`/api/stats/conversion?${withParam(query, "group_by", groupBy)}`);

export const fetchRecentCalls = (query: URLSearchParams, limit: number) =>
  request<Call[]>(`/api/calls?${withParam(query, "limit", String(limit))}`);

export const CALL_STREAM_URL = "/api/calls/stream";

function withParam(query: URLSearchParams, name: string, value: string): URLSearchParams {
  const copy = new URLSearchParams(query);
  copy.set(name, value);
  return copy;
}
