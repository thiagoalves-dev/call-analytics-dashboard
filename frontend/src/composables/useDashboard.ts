import { computed, onBeforeUnmount, reactive, ref, watch } from "vue";
import { fetchCampaigns, fetchConversion, fetchRecentCalls, fetchVolume } from "../api/endpoints";
import type { Call, Campaign, ConversionGrouping, ConversionResponse, Granularity, VolumeResponse } from "../api/types";
import { callMatchesFilters, defaultFilters, effectiveGranularity, rangeFor, toQueryParams } from "../lib/filters";

const FEED_SIZE = 50;
export const LIVE_REFRESH_MS = 10_000;
const SLIDING_WINDOW_REFRESH_MS = 60_000;

const newestFirst = (first: Call, second: Call) => Date.parse(second.ended_at) - Date.parse(first.ended_at);

function mergeNewest(incoming: Call[], current: Call[]): Call[] {
  const unique = new Map([...current, ...incoming].map((call) => [call.id, call]));
  return [...unique.values()].sort(newestFirst).slice(0, FEED_SIZE);
}

export function useDashboard() {
  const filters = reactive(defaultFilters());
  const requestedGranularity = ref<Granularity>("hour");
  const conversionGrouping = ref<ConversionGrouping>("campaign");
  const now = ref(new Date());

  const campaigns = ref<Campaign[]>([]);
  const volume = ref<VolumeResponse | null>(null);
  const conversion = ref<ConversionResponse | null>(null);
  const feed = ref<Call[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  let pendingCalls: Call[] = [];

  const range = computed(() => rangeFor(filters, now.value));
  const granularity = computed(() => effectiveGranularity(requestedGranularity.value, range.value));
  const query = computed(() => toQueryParams(filters, range.value));

  async function loadCampaigns() {
    campaigns.value = await fetchCampaigns();
  }

  async function loadCharts() {
    const [volumeResponse, conversionResponse] = await Promise.all([
      fetchVolume(query.value, granularity.value),
      fetchConversion(query.value, conversionGrouping.value),
    ]);
    volume.value = volumeResponse;
    conversion.value = conversionResponse;
  }

  async function loadFeed() {
    pendingCalls = [];
    feed.value = await fetchRecentCalls(query.value, FEED_SIZE);
  }

  async function reload() {
    now.value = new Date();
    loading.value = true;
    error.value = null;
    try {
      await Promise.all([loadCharts(), loadFeed()]);
    } catch (failure) {
      error.value = failure instanceof Error ? failure.message : String(failure);
    } finally {
      loading.value = false;
    }
  }

  let liveRefreshTimer: ReturnType<typeof setTimeout> | null = null;

  function scheduleLiveRefresh() {
    if (liveRefreshTimer) return;
    liveRefreshTimer = setTimeout(applyLiveRefresh, LIVE_REFRESH_MS);
  }

  async function applyLiveRefresh() {
    liveRefreshTimer = null;
    feed.value = mergeNewest(pendingCalls, feed.value);
    pendingCalls = [];
    now.value = new Date();
    await loadCharts().catch(() => undefined);
  }

  function receiveLiveCall(call: Call) {
    if (!callMatchesFilters(call, filters)) return;
    pendingCalls.push(call);
    scheduleLiveRefresh();
  }

  const slidingWindow = setInterval(reload, SLIDING_WINDOW_REFRESH_MS);
  onBeforeUnmount(() => {
    clearInterval(slidingWindow);
    if (liveRefreshTimer) clearTimeout(liveRefreshTimer);
  });

  watch([() => ({ ...filters }), requestedGranularity, conversionGrouping], reload, { deep: true });

  return {
    filters,
    requestedGranularity,
    granularity,
    conversionGrouping,
    range,
    campaigns,
    volume,
    conversion,
    feed,
    loading,
    error,
    loadCampaigns,
    reload,
    receiveLiveCall,
  };
}
