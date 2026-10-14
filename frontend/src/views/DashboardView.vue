<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import FilterBar from "../components/FilterBar.vue";
import KpiCards from "../components/KpiCards.vue";
import LiveFeed from "../components/LiveFeed.vue";
import ConversionChart from "../components/charts/ConversionChart.vue";
import VolumeChart from "../components/charts/VolumeChart.vue";
import { LIVE_REFRESH_MS, useDashboard } from "../composables/useDashboard";
import { useLiveCalls } from "../composables/useLiveCalls";
import { useSession } from "../composables/useSession";
import { conversionChartData, volumeChartData } from "../lib/chartData";
import { hourlyViewAllowed } from "../lib/filters";

const router = useRouter();
const { currentUser, signOut } = useSession();
const dashboard = useDashboard();
const { filters, requestedGranularity, granularity, conversionGrouping, range, volume, conversion, feed } = dashboard;
const { streamState } = useLiveCalls(dashboard.receiveLiveCall, dashboard.reload);
const refreshSeconds = LIVE_REFRESH_MS / 1000;

const volumeData = computed(() => volume.value && volumeChartData(volume.value));
const conversionData = computed(() => conversion.value && conversionChartData(conversion.value.rows));

async function logOut() {
  await signOut();
  await router.push("/login");
}

onMounted(async () => {
  await dashboard.loadCampaigns();
  await dashboard.reload();
});
</script>

<template>
  <div class="dashboard">
    <header class="top">
      <div>
        <h1>{{ currentUser?.account_name }}</h1>
        <span class="muted">Inbound call performance · times in {{ currentUser?.timezone }}</span>
        <p class="refresh-note">Everything on this page updates every {{ refreshSeconds }} seconds.</p>
      </div>
      <div class="actions">
        <span class="muted">{{ currentUser?.name }}</span>
        <button type="button" @click="logOut">Sign out</button>
      </div>
    </header>

    <FilterBar v-model:filters="filters" :campaigns="dashboard.campaigns.value" />
    <p v-if="dashboard.error.value" class="error">{{ dashboard.error.value }}</p>
    <KpiCards :rows="conversion?.rows ?? []" :outcome-filtered="filters.statuses.length > 0" />

    <section class="panel">
      <header>
        <h2>Call volume</h2>
        <div class="toggle">
          <button :class="{ active: granularity === 'hour' }" :disabled="!hourlyViewAllowed(range)" @click="requestedGranularity = 'hour'">
            Hourly
          </button>
          <button :class="{ active: granularity === 'day' }" @click="requestedGranularity = 'day'">Daily</button>
        </div>
      </header>
      <div class="chart tall">
        <VolumeChart v-if="volumeData" :data="volumeData" />
      </div>
    </section>

    <div class="columns">
      <section class="panel">
        <header>
          <h2>Conversion rate</h2>
          <div class="toggle">
            <button :class="{ active: conversionGrouping === 'campaign' }" @click="conversionGrouping = 'campaign'">By campaign</button>
            <button :class="{ active: conversionGrouping === 'source' }" @click="conversionGrouping = 'source'">By source</button>
          </div>
        </header>
        <p class="muted note">Converted calls ÷ all calls. The outcome filter doesn't apply here.</p>
        <div class="chart">
          <ConversionChart v-if="conversionData" :data="conversionData" />
        </div>
      </section>
      <LiveFeed :calls="feed" :timezone="currentUser?.timezone ?? 'UTC'" :stream-state="streamState" />
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1280px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
h1 {
  margin: 0;
  font-size: 22px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.actions button {
  font: inherit;
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 6px;
  padding: 5px 10px;
  cursor: pointer;
}
.muted {
  color: var(--muted);
  font-size: 13px;
}
.refresh-note {
  margin: 4px 0 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
}
.note {
  margin: 0 0 8px;
}
.error {
  color: #e5484d;
  margin: 0;
}
.columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
  gap: 16px;
}
@media (max-width: 900px) {
  .columns {
    grid-template-columns: minmax(0, 1fr);
  }
}
.chart {
  position: relative;
  height: 340px;
}
.chart.tall {
  height: 320px;
}
.chart > * {
  height: 100%;
}
.toggle {
  display: flex;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}
.toggle button {
  font: inherit;
  font-size: 13px;
  background: var(--background);
  color: var(--text);
  border: none;
  padding: 5px 12px;
  cursor: pointer;
}
.toggle button.active {
  background: var(--accent);
  color: white;
}
.toggle button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
