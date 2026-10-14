<script setup lang="ts">
import type { Campaign, CallStatus } from "../api/types";
import { ALL_STATUSES, type Filters } from "../lib/filters";
import { STATUS_LABELS } from "../lib/statusColors";
import CampaignPicker from "./CampaignPicker.vue";

defineProps<{ campaigns: Campaign[] }>();
const filters = defineModel<Filters>("filters", { required: true });

const PRESETS = [
  { value: "24h", label: "Last 24 hours" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
  { value: "90d", label: "Last 90 days" },
  { value: "custom", label: "Custom range" },
] as const;

function toggleStatus(status: CallStatus) {
  const statuses = filters.value.statuses;
  filters.value.statuses = statuses.includes(status) ? statuses.filter((item) => item !== status) : [...statuses, status];
}
</script>

<template>
  <section class="filters">
    <label>
      <span>Date range</span>
      <select v-model="filters.preset">
        <option v-for="preset in PRESETS" :key="preset.value" :value="preset.value">{{ preset.label }}</option>
      </select>
    </label>
    <template v-if="filters.preset === 'custom'">
      <label>
        <span>From</span>
        <input v-model="filters.customStart" type="date" />
      </label>
      <label>
        <span>To</span>
        <input v-model="filters.customEnd" type="date" />
      </label>
    </template>
    <div class="field">
      <span>Campaigns</span>
      <CampaignPicker v-model="filters.campaignIds" :campaigns="campaigns" />
    </div>
    <div class="outcomes">
      <span>Outcome</span>
      <div class="chips">
        <button
          v-for="status in ALL_STATUSES"
          :key="status"
          type="button"
          :class="{ active: filters.statuses.includes(status) }"
          @click="toggleStatus(status)"
        >
          {{ STATUS_LABELS[status] }}
        </button>
      </div>
    </div>
    <button
      v-if="filters.campaignIds.length || filters.statuses.length"
      type="button"
      class="clear"
      @click="(filters.campaignIds = []), (filters.statuses = [])"
    >
      Clear filters
    </button>
  </section>
</template>

<style scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 16px;
}
label,
.field,
.outcomes {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
  color: var(--muted);
}
select,
input {
  font: inherit;
  color: var(--text);
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 8px;
}
.chips {
  display: flex;
  gap: 6px;
}
.chips button,
.clear {
  font: inherit;
  border: 1px solid var(--border);
  background: var(--background);
  color: var(--text);
  border-radius: 999px;
  padding: 5px 12px;
  cursor: pointer;
}
.chips button.active {
  background: var(--accent);
  border-color: var(--accent);
  color: white;
}
.clear {
  border-style: dashed;
}
</style>
