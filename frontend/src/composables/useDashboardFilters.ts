import { computed, reactive, ref } from "vue";
import type { ConversionGrouping, Granularity } from "../api/types";
import { defaultFilters, effectiveGranularity, rangeFor, toQueryParams } from "../lib/filters";

export function useDashboardFilters() {
  const filters = reactive(defaultFilters());
  const requestedGranularity = ref<Granularity>("hour");
  const conversionGrouping = ref<ConversionGrouping>("campaign");
  const now = ref(new Date());
  const range = computed(() => rangeFor(filters, now.value));
  const granularity = computed(() => effectiveGranularity(requestedGranularity.value, range.value));
  const query = computed(() => toQueryParams(filters, range.value));
  const refreshNow = () => (now.value = new Date());
  return { filters, requestedGranularity, conversionGrouping, range, granularity, query, refreshNow };
}

export type DashboardFilters = ReturnType<typeof useDashboardFilters>;
