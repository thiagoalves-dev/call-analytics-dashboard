import type { CallStatus } from "../api/types";

export const STATUS_COLORS: Record<CallStatus, string> = {
  missed: "#e5484d",
  connected: "#8b95a7",
  converted: "#12a594",
};

export const STATUS_LABELS: Record<CallStatus, string> = {
  missed: "Missed",
  connected: "Connected",
  converted: "Converted",
};
