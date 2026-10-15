import type { Call } from "../api/types";
import { callMatchesFilters } from "../lib/filters";
import type { LiveCallBuffer } from "../lib/liveCallBuffer";
import type { DashboardFilters } from "./useDashboardFilters";
import { useInterval } from "./useTimers";

export const LIVE_REFRESH_MS = 10_000;

interface LiveMergeTargets {
  mergeLiveCalls: () => void;
  refreshData: () => Promise<unknown>;
}

export function useLiveMerge(view: DashboardFilters, liveCalls: LiveCallBuffer, targets: LiveMergeTargets) {
  async function applyLiveRefresh() {
    targets.mergeLiveCalls();
    view.refreshNow();
    await targets.refreshData();
  }
  useInterval(applyLiveRefresh, LIVE_REFRESH_MS);
  return function receiveLiveCall(call: Call) {
    if (callMatchesFilters(call, view.filters)) liveCalls.hold(call);
  };
}
