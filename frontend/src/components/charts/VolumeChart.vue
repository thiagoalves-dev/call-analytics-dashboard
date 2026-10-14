<script setup lang="ts">
import { BarElement, CategoryScale, Chart, Legend, LinearScale, Tooltip } from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { VolumeChartData } from "../../lib/chartData";

Chart.register(BarElement, CategoryScale, LinearScale, Legend, Tooltip);

const props = defineProps<{ data: VolumeChartData }>();

const chartData = computed(() => ({
  labels: props.data.labels,
  datasets: props.data.series.map((series) => ({ label: series.label, data: series.values, backgroundColor: series.color })),
}));

const options = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false as const,
  interaction: { mode: "index" as const, intersect: false },
  scales: { x: { stacked: true, ticks: { maxTicksLimit: 12 } }, y: { stacked: true, beginAtZero: true } },
};
</script>

<template>
  <Bar :data="chartData" :options="options" />
</template>
