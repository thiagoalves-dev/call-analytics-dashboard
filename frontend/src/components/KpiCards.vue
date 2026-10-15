<script setup lang="ts">
import { computed } from "vue";
import type { ConversionRow } from "../api/types";
import { formatCount, formatPercent } from "../lib/format";

const props = defineProps<{ rows: ConversionRow[]; outcomeFiltered: boolean }>();

const MISSED_RATE_WARNING = 0.2;

const ICONS = {
  calls: "M5.5 3h2l1 3-1.5 1a8 8 0 0 0 3.5 3.5l1-1.5 3 1v2a1.5 1.5 0 0 1-1.5 1.5A10.5 10.5 0 0 1 2.5 4.5 1.5 1.5 0 0 1 4 3Z",
  conversions: "M3 8.5 6.5 12 13 4.5",
  conversionRate: "M2.5 12.5 6 9l2.5 2.5L13.5 6M10 6h3.5v3.5",
  missedRate: "M4.5 4.5l7 7M11.5 4.5l-7 7",
};

const totals = computed(() =>
  props.rows.reduce(
    (sum, row) => ({ calls: sum.calls + row.calls, missed: sum.missed + row.missed, converted: sum.converted + row.converted }),
    { calls: 0, missed: 0, converted: 0 },
  ),
);

const rate = (part: number) => (totals.value.calls ? part / totals.value.calls : null);

const cards = computed(() => [
  { label: "Calls", value: formatCount(totals.value.calls), icon: ICONS.calls, tone: "accent", warning: false },
  { label: "Conversions", value: formatCount(totals.value.converted), icon: ICONS.conversions, tone: "accent", warning: false },
  {
    label: "Conversion rate",
    value: formatPercent(rate(totals.value.converted)),
    icon: ICONS.conversionRate,
    tone: "converted",
    warning: false,
  },
  {
    label: "Missed rate",
    value: formatPercent(rate(totals.value.missed)),
    icon: ICONS.missedRate,
    tone: "missed",
    warning: (rate(totals.value.missed) ?? 0) > MISSED_RATE_WARNING,
  },
]);
</script>

<template>
  <section class="kpis">
    <div v-for="card in cards" :key="card.label" class="kpi">
      <div class="heading">
        <span class="icon" :class="card.tone">
          <svg viewBox="0 0 16 16" aria-hidden="true"><path :d="card.icon" /></svg>
        </span>
        <span class="label">{{ card.label }}</span>
      </div>
      <strong :class="{ warning: card.warning }">{{ card.value }}</strong>
    </div>
    <p v-if="outcomeFiltered" class="note">These totals cover every outcome; the outcome filter applies to the volume chart and the feed.</p>
  </section>
</template>

<style scoped>
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.kpi {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}
.heading {
  display: flex;
  align-items: center;
  gap: 10px;
}
.icon {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
}
.icon svg {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.icon.accent {
  color: var(--accent-ink);
  background: var(--accent-soft);
}
.icon.converted {
  color: var(--converted-ink);
  background: var(--converted-soft);
}
.icon.missed {
  color: var(--missed-ink);
  background: var(--missed-soft);
}
.label {
  color: var(--muted);
  font-size: 13px;
  font-weight: 500;
}
strong {
  font-size: 30px;
  line-height: 1.1;
  font-weight: 600;
  letter-spacing: -0.025em;
  font-variant-numeric: tabular-nums;
}
.warning {
  color: var(--missed-ink);
}
.note {
  grid-column: 1 / -1;
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}
@media (max-width: 640px) {
  .kpis {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .kpi {
    padding: 14px;
  }
  strong {
    font-size: 22px;
  }
}
</style>
