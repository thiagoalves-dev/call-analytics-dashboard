<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import FilterBar from "../components/FilterBar.vue";
import KpiCards from "../components/KpiCards.vue";
import LiveFeed from "../components/LiveFeed.vue";
import LogoMark from "../components/LogoMark.vue";
import ConversionChart from "../components/charts/ConversionChart.vue";
import VolumeChart from "../components/charts/VolumeChart.vue";
import { useDashboard } from "../composables/useDashboard";
import { useLiveCalls } from "../composables/useLiveCalls";
import { LIVE_REFRESH_MS } from "../composables/useLiveMerge";
import { useSession } from "../composables/useSession";
import { conversionChartData, volumeChartData } from "../lib/chartData";
import { MAX_HOURLY_RANGE_IN_DAYS, hourlyViewAllowed } from "../lib/filters";
import { initialsOf } from "../lib/format";

const MS_PER_SECOND = 1000;
const HOURLY_UNAVAILABLE_REASON = `Hourly view is available for ranges up to ${MAX_HOURLY_RANGE_IN_DAYS} days`;

const router = useRouter();
const { currentUser, signOut, endSession } = useSession();
const dashboard = useDashboard(leaveExpiredSession);
const { filters, requestedGranularity, granularity, conversionGrouping, range, volume, conversion, feed } = dashboard;
const liveCalls = useLiveCalls(dashboard.receiveLiveCall, dashboard.reload);
const { streamState } = liveCalls;
const refreshSeconds = LIVE_REFRESH_MS / MS_PER_SECOND;
const initials = computed(() => initialsOf(currentUser.value?.name ?? ""));
const hourlyAllowed = computed(() => hourlyViewAllowed(range.value));

const volumeData = computed(() => volume.value && volumeChartData(volume.value));
const conversionData = computed(() => conversion.value && conversionChartData(conversion.value.rows));

async function logOut() {
  await signOut();
  await router.push("/login");
}

function leaveExpiredSession() {
  endSession();
  liveCalls.stop();
  router.replace("/login");
}

onMounted(dashboard.start);
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="brand">
        <LogoMark />
        <span class="product">Call Analytics</span>
        <span class="separator" aria-hidden="true">/</span>
        <span class="company">{{ currentUser?.account_name }}</span>
      </div>
      <p class="refresh-note">
        <span class="pulse-dot"></span>Everything on this page updates every {{ refreshSeconds }} seconds.
      </p>
      <div class="account">
        <span class="avatar" :title="currentUser?.name" aria-hidden="true">{{ initials }}</span>
        <span class="user-name">{{ currentUser?.name }}</span>
        <button type="button" class="sign-out" @click="logOut">Sign out</button>
      </div>
    </header>

    <main class="dashboard">
      <div class="heading">
        <h1>Call performance</h1>
        <span class="muted">Inbound calls · times in {{ currentUser?.timezone }}</span>
      </div>

      <FilterBar v-model:filters="filters" :campaigns="dashboard.campaigns.value" />
      <p v-if="dashboard.error.value" class="error" role="alert">{{ dashboard.error.value }}</p>
      <KpiCards :rows="conversion?.rows ?? []" :outcome-filtered="filters.statuses.length > 0" />

      <section class="panel">
        <header>
          <h2>Call volume</h2>
          <div class="segmented" role="group" aria-label="Volume granularity">
            <button
              type="button"
              :class="{ active: granularity === 'hour' }"
              :aria-pressed="granularity === 'hour'"
              :disabled="!hourlyAllowed"
              :title="hourlyAllowed ? undefined : HOURLY_UNAVAILABLE_REASON"
              @click="requestedGranularity = 'hour'"
            >
              Hourly
            </button>
            <button
              type="button"
              :class="{ active: granularity === 'day' }"
              :aria-pressed="granularity === 'day'"
              @click="requestedGranularity = 'day'"
            >
              Daily
            </button>
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
            <div class="segmented" role="group" aria-label="Conversion grouping">
              <button
                type="button"
                :class="{ active: conversionGrouping === 'campaign' }"
                :aria-pressed="conversionGrouping === 'campaign'"
                @click="conversionGrouping = 'campaign'"
              >
                By campaign
              </button>
              <button
                type="button"
                :class="{ active: conversionGrouping === 'source' }"
                :aria-pressed="conversionGrouping === 'source'"
                @click="conversionGrouping = 'source'"
              >
                By source
              </button>
            </div>
          </header>
          <p class="muted note">Converted calls ÷ all calls. The outcome filter doesn't apply here.</p>
          <div class="chart">
            <ConversionChart v-if="conversionData" :data="conversionData" />
          </div>
        </section>
        <LiveFeed :calls="feed" :timezone="currentUser?.timezone ?? 'UTC'" :stream-state="streamState" />
      </div>
    </main>
  </div>
</template>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px max(24px, calc((100% - 1280px) / 2 + 24px));
  background: color-mix(in srgb, var(--surface) 85%, transparent);
  backdrop-filter: saturate(180%) blur(12px);
  border-bottom: 1px solid var(--border);
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  font-size: 14px;
}
.product {
  font-weight: 600;
  letter-spacing: -0.01em;
  white-space: nowrap;
}
.separator {
  color: var(--border-strong);
  font-size: 18px;
  font-weight: 300;
}
.company {
  color: var(--muted);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.refresh-note {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 0 auto;
  font-size: 12px;
  font-weight: 500;
  color: var(--muted);
}
.refresh-note .pulse-dot {
  color: var(--converted);
}
.account {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 16px;
  border-left: 1px solid var(--border);
}
.avatar {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  color: var(--accent-ink);
  background: var(--accent-soft);
}
.user-name {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}
.sign-out {
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 4px 10px;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s ease, border-color 0.15s ease;
}
.sign-out:hover {
  color: var(--text);
  border-color: var(--border-strong);
}
.dashboard {
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px 48px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.heading {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.muted {
  color: var(--muted);
  font-size: 13px;
}
.note {
  margin: -8px 0 12px;
}
.error {
  color: var(--missed-ink);
  background: var(--missed-soft);
  border-radius: 8px;
  padding: 10px 14px;
  margin: 0;
}
.columns {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
  gap: 20px;
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
@media (max-width: 900px) {
  .columns {
    grid-template-columns: minmax(0, 1fr);
  }
  .user-name {
    display: none;
  }
}
@media (max-width: 640px) {
  .topbar {
    flex-wrap: wrap;
    padding: 10px 16px;
    row-gap: 8px;
  }
  .product,
  .separator {
    display: none;
  }
  .company {
    color: var(--text);
    font-weight: 600;
  }
  .account {
    margin-left: auto;
    padding-left: 0;
    border-left: none;
  }
  .refresh-note {
    order: 1;
    flex-basis: 100%;
    margin: 0;
  }
  .dashboard {
    padding: 20px 16px 40px;
    gap: 16px;
  }
  .chart,
  .chart.tall {
    height: 280px;
  }
}
</style>
