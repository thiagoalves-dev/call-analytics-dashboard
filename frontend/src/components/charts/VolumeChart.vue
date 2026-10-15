<script setup lang="ts">
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import { volumeChartSummary, type StatusSeries, type VolumeChartData } from "../../lib/chartData";
import { chartColors, tooltipStyle } from "../../lib/chartTheme";
import { formatCompact } from "../../lib/format";

const props = defineProps<{ data: VolumeChartData }>();

const TOP_CORNER_RADIUS = { topLeft: 3, topRight: 3, bottomLeft: 0, bottomRight: 0 };
const CATEGORY_WIDTH_SHARE = 0.82;
const BAR_WIDTH_SHARE = 0.9;
const X_TICK_SKIP_PADDING = 16;
const MAX_Y_TICKS = 6;
const Y_TICK_PADDING = 8;

function dataset(series: StatusSeries, index: number) {
  const isTopOfStack = index === props.data.series.length - 1;
  return {
    label: series.label,
    data: series.values,
    backgroundColor: series.color,
    hoverBackgroundColor: series.color,
    borderRadius: isTopOfStack ? TOP_CORNER_RADIUS : 0,
    borderSkipped: false,
    categoryPercentage: CATEGORY_WIDTH_SHARE,
    barPercentage: BAR_WIDTH_SHARE,
  };
}

const chartData = computed(() => ({
  labels: props.data.labels,
  datasets: props.data.series.map(dataset),
}));

function scales() {
  const colors = chartColors();
  return {
    x: {
      stacked: true,
      grid: { display: false },
      border: { display: false },
      ticks: { color: colors.muted, maxRotation: 0, autoSkipPadding: X_TICK_SKIP_PADDING },
    },
    y: {
      stacked: true,
      beginAtZero: true,
      border: { display: false },
      grid: { color: colors.grid },
      ticks: {
        color: colors.muted,
        maxTicksLimit: MAX_Y_TICKS,
        padding: Y_TICK_PADDING,
        callback: (value: string | number) => formatCompact(Number(value)),
      },
    },
  };
}

const summary = computed(() => volumeChartSummary(props.data));

const options = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false as const,
  interaction: { mode: "index" as const, intersect: false },
  scales: scales(),
  plugins: { tooltip: tooltipStyle() },
}));
</script>

<template>
  <div class="volume">
    <ul class="legend">
      <li v-for="series in data.series" :key="series.status">
        <span class="swatch" :style="{ background: series.color }"></span>{{ series.label }}
      </li>
    </ul>
    <div class="canvas">
      <Bar :data="chartData" :options="options" :aria-label="summary" />
    </div>
  </div>
</template>

<style scoped>
.volume {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: 12px;
  color: var(--muted);
}
.legend li {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.swatch {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.canvas {
  position: relative;
  flex: 1;
  min-height: 0;
}
</style>
