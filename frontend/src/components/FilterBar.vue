<script setup lang="ts">
import type { Campaign, CallStatus } from "../api/types";
import { ALL_STATUSES, type Filters } from "../lib/filters";
import { STATUS_LABELS } from "../lib/statusColors";
import CampaignPicker from "./CampaignPicker.vue";

defineProps<{ campaigns: Campaign[] }>();
const filters = defineModel<Filters>("filters", { required: true });

const PRESETS = [
  { value: "24h", shortLabel: "24h", label: "Last 24 hours" },
  { value: "7d", shortLabel: "7d", label: "Last 7 days" },
  { value: "30d", shortLabel: "30d", label: "Last 30 days" },
  { value: "90d", shortLabel: "90d", label: "Last 90 days" },
] as const;

function toggleStatus(status: CallStatus) {
  const statuses = filters.value.statuses;
  filters.value.statuses = statuses.includes(status) ? statuses.filter((item) => item !== status) : [...statuses, status];
}
</script>

<template>
  <section class="filters" aria-label="Filters">
    <div class="segmented" role="group" aria-label="Date range">
      <button
        v-for="preset in PRESETS"
        :key="preset.value"
        type="button"
        :title="preset.label"
        :aria-label="preset.label"
        :aria-pressed="filters.preset === preset.value"
        :class="{ active: filters.preset === preset.value }"
        @click="filters.preset = preset.value"
      >
        {{ preset.shortLabel }}
      </button>
    </div>
    <CampaignPicker v-model="filters.campaignIds" :campaigns="campaigns" />
    <span class="divider" aria-hidden="true"></span>
    <div class="chips" role="group" aria-label="Outcome">
      <button
        v-for="status in ALL_STATUSES"
        :key="status"
        type="button"
        :class="[status, { active: filters.statuses.includes(status) }]"
        :aria-pressed="filters.statuses.includes(status)"
        @click="toggleStatus(status)"
      >
        {{ STATUS_LABELS[status] }}
      </button>
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
  align-items: center;
  gap: 10px;
}
.divider {
  width: 1px;
  height: 20px;
  background: var(--border-strong);
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chips button {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 500;
  color: var(--muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 5px 12px 5px 10px;
  cursor: pointer;
  transition: color 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
}
.chips button::before {
  content: "";
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--chip-color);
}
.chips button:hover {
  color: var(--text);
  border-color: var(--border-strong);
}
.chips .missed {
  --chip-color: var(--missed);
  --chip-soft: var(--missed-soft);
  --chip-ink: var(--missed-ink);
}
.chips .connected {
  --chip-color: var(--connected);
  --chip-soft: var(--connected-soft);
  --chip-ink: var(--connected-ink);
}
.chips .converted {
  --chip-color: var(--converted);
  --chip-soft: var(--converted-soft);
  --chip-ink: var(--converted-ink);
}
.chips button.active {
  color: var(--chip-ink);
  background: var(--chip-soft);
  border-color: var(--chip-color);
}
.clear {
  font-size: 13px;
  font-weight: 500;
  color: var(--accent-ink);
  background: none;
  border: none;
  padding: 5px 6px;
  cursor: pointer;
}
.clear:hover {
  text-decoration: underline;
}
@media (max-width: 640px) {
  .divider {
    display: none;
  }
}
</style>
