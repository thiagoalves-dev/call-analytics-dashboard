import type { CallStatus } from "../api/types";

export const STATUS_COLORS: Record<CallStatus, string> = {
  missed: "#ec5f67",
  connected: "#9aa7bd",
  converted: "#26a86b",
};

export const STATUS_LABELS: Record<CallStatus, string> = {
  missed: "Missed",
  connected: "Connected",
  converted: "Converted",
};
