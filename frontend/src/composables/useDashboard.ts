import { watch } from "vue";
import { LiveCallBuffer } from "../lib/liveCallBuffer";
import { useCampaigns, useCharts, useFeed } from "./useDashboardData";
import { useDashboardFilters } from "./useDashboardFilters";
import { useLiveMerge } from "./useLiveMerge";
import { useLoadStatus } from "./useLoadStatus";

export function useDashboard(onUnauthenticated: () => void) {
  const view = useDashboardFilters();
  const liveCalls = new LiveCallBuffer();
  const { campaigns, loadCampaigns } = useCampaigns();
  const { volume, conversion, loadCharts } = useCharts(view);
  const { feed, loadFeed, mergeLiveCalls } = useFeed(view, liveCalls);
  const { error, clearError, reportFailure, reportUnauthenticated } = useLoadStatus(onUnauthenticated);

  async function reload() {
    view.refreshNow();
    clearError();
    await Promise.all([loadCharts(), loadFeed()]).catch(reportFailure);
  }
  const start = () => Promise.all([loadCampaigns().catch(reportFailure), reload()]);
  const liveMergeTargets = { mergeLiveCalls, loadCharts, onChartFailure: reportUnauthenticated };
  const receiveLiveCall = useLiveMerge(view, liveCalls, liveMergeTargets);
  watch([() => ({ ...view.filters }), view.requestedGranularity, view.conversionGrouping], reload, { deep: true });
  return { ...view, campaigns, volume, conversion, feed, error, reload, start, receiveLiveCall };
}
