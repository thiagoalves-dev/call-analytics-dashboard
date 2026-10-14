<script setup lang="ts">
import { BarElement, CategoryScale, Chart, LinearScale, Tooltip, type TooltipItem } from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import type { ConversionChartData } from "../../lib/chartData";

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip);

const props = defineProps<{ data: ConversionChartData }>();

const chartData = computed(() => ({
  labels: props.data.labels,
  datasets: [{ label: "Conversion rate", data: props.data.ratesInPercent, backgroundColor: "#12a594" }],
}));

const options = computed(() => ({
  indexAxis: "y" as const,
  responsive: true,
  maintainAspectRatio: false,
  animation: false as const,
  scales: { x: { beginAtZero: true, ticks: { callback: (value: string | number) => `${value}%` } } },
  plugins: {
    tooltip: {
      callbacks: {
        label: (item: TooltipItem<"bar">) => `${item.formattedValue}% of ${props.data.calls[item.dataIndex]} calls`,
      },
    },
  },
}));
</script>

<template>
  <Bar :data="chartData" :options="options" />
</template>
