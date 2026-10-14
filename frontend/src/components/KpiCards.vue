<script setup lang="ts">
import { computed } from "vue";
import type { ConversionRow } from "../api/types";
import { formatCount, formatPercent } from "../lib/format";

const props = defineProps<{ rows: ConversionRow[]; outcomeFiltered: boolean }>();

const totals = computed(() =>
  props.rows.reduce(
    (sum, row) => ({ calls: sum.calls + row.calls, missed: sum.missed + row.missed, converted: sum.converted + row.converted }),
    { calls: 0, missed: 0, converted: 0 },
  ),
);

const rate = (part: number) => (totals.value.calls ? part / totals.value.calls : null);
</script>

<template>
  <section class="kpis">
    <div class="kpi">
      <span class="label">Calls</span>
      <strong>{{ formatCount(totals.calls) }}</strong>
    </div>
    <div class="kpi">
      <span class="label">Conversions</span>
      <strong>{{ formatCount(totals.converted) }}</strong>
    </div>
    <div class="kpi">
      <span class="label">Conversion rate</span>
      <strong>{{ formatPercent(rate(totals.converted)) }}</strong>
    </div>
    <div class="kpi">
      <span class="label">Missed rate</span>
      <strong :class="{ warning: (rate(totals.missed) ?? 0) > 0.2 }">{{ formatPercent(rate(totals.missed)) }}</strong>
    </div>
    <p v-if="outcomeFiltered" class="note">These totals cover every outcome; the outcome filter applies to the volume chart and the feed.</p>
  </section>
</template>

<style scoped>
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}
.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.label {
  color: var(--muted);
  font-size: 13px;
}
strong {
  font-size: 26px;
}
.note {
  grid-column: 1 / -1;
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
.warning {
  color: #e5484d;
}
</style>
