<script setup lang="ts">
import { BarElement, CategoryScale, Chart, LinearScale, Tooltip } from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { StatusSeries, VolumeChartData } from "../../lib/chartData";
import { chartColors, tooltipStyle } from "../../lib/chartTheme";
import { formatCompact } from "../../lib/format";

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip);

const props = defineProps<{ data: VolumeChartData }>();

const TOP_CORNER_RADIUS = { topLeft: 3, topRight: 3, bottomLeft: 0, bottomRight: 0 };

function dataset(series: StatusSeries, index: number) {
  const isTopOfStack = index === props.data.series.length - 1;
  return {
    label: series.label,
    data: series.values,
    backgroundColor: series.color,
    hoverBackgroundColor: series.color,
    borderRadius: isTopOfStack ? TOP_CORNER_RADIUS : 0,
    borderSkipped: false,
    categoryPercentage: 0.82,
    barPercentage: 0.9,
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
      ticks: { color: colors.muted, maxRotation: 0, autoSkipPadding: 16 },
    },
    y: {
      stacked: true,
      beginAtZero: true,
      border: { display: false },
      grid: { color: colors.grid },
      ticks: { color: colors.muted, maxTicksLimit: 6, padding: 8, callback: (value: string | number) => formatCompact(Number(value)) },
    },
  };
}

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
      <Bar :data="chartData" :options="options" />
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
