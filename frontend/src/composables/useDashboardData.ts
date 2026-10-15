import { ref } from "vue";
import { fetchCampaigns, fetchConversion, fetchRecentCalls, fetchVolume } from "../api/endpoints";
import type { Call, Campaign, ConversionResponse, VolumeResponse } from "../api/types";
import { FEED_SIZE } from "../lib/feed";
import { createLatestResponseGuard } from "../lib/latestResponse";
import type { LiveCallBuffer } from "../lib/liveCallBuffer";
import type { DashboardFilters } from "./useDashboardFilters";

type ChartResponses = [VolumeResponse, ConversionResponse];

export function useCampaigns() {
  const campaigns = ref<Campaign[]>([]);
  async function loadCampaigns() {
    campaigns.value = await fetchCampaigns();
  }
  return { campaigns, loadCampaigns };
}

export function useCharts(view: DashboardFilters) {
  const volume = ref<VolumeResponse | null>(null);
  const conversion = ref<ConversionResponse | null>(null);
  const applyLatest = createLatestResponseGuard();
  function applyCharts([volumeResponse, conversionResponse]: ChartResponses) {
    volume.value = volumeResponse;
    conversion.value = conversionResponse;
  }
  const loadCharts = () => applyLatest(() => fetchCharts(view), applyCharts);
  return { volume, conversion, loadCharts };
}

export function useFeed(view: DashboardFilters, liveCalls: LiveCallBuffer) {
  const feed = ref<Call[]>([]);
  const applyLatest = createLatestResponseGuard();
  function loadFeed() {
    liveCalls.startFeedRequest();
    const request = () => fetchRecentCalls(view.query.value, FEED_SIZE);
    return applyLatest(request, (calls) => (feed.value = liveCalls.mergeIntoFeedResponse(calls)));
  }
  const mergeLiveCalls = () => (feed.value = liveCalls.mergeInto(feed.value));
  return { feed, loadFeed, mergeLiveCalls };
}

function fetchCharts(view: DashboardFilters): Promise<ChartResponses> {
  return Promise.all([
    fetchVolume(view.query.value, view.granularity.value),
    fetchConversion(view.query.value, view.conversionGrouping.value),
  ]);
}
