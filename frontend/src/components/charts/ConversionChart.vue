<script setup lang="ts">
import { BarElement, CategoryScale, Chart, LinearScale, Tooltip, type Plugin, type TooltipItem } from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";
import { conversionChartSummary, type ConversionChartData } from "../../lib/chartData";
import { CHART_FONT_FAMILY, chartColors, tooltipStyle } from "../../lib/chartTheme";
import { STATUS_COLORS } from "../../lib/statusColors";

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip);

const props = defineProps<{ data: ConversionChartData }>();

const VALUE_LABEL_GAP = 8;
const VALUE_LABEL_SPACE = 48;
const LABEL_SEPARATOR = " - ";
const VALUE_LABEL_FONT = "600 12px";
const BAR_CORNER_RADIUS = 6;
const MAX_BAR_THICKNESS = 24;
const CATEGORY_WIDTH_SHARE = 0.7;
const Y_TICK_PADDING = 8;

const valueLabels: Plugin<"bar"> = {
  id: "conversionValueLabels",
  afterDatasetsDraw(chart) {
    const { ctx } = chart;
    ctx.save();
    ctx.font = `${VALUE_LABEL_FONT} ${CHART_FONT_FAMILY}`;
    ctx.fillStyle = chartColors().text;
    ctx.textBaseline = "middle";
    chart.getDatasetMeta(0).data.forEach((bar, index) => {
      ctx.fillText(`${props.data.ratesInPercent[index]}%`, bar.x + VALUE_LABEL_GAP, bar.y);
    });
    ctx.restore();
  },
};

const chartData = computed(() => ({
  labels: props.data.labels,
  datasets: [
    {
      label: "Conversion rate",
      data: props.data.ratesInPercent,
      backgroundColor: STATUS_COLORS.converted,
      hoverBackgroundColor: STATUS_COLORS.converted,
      borderRadius: BAR_CORNER_RADIUS,
      borderSkipped: false,
      maxBarThickness: MAX_BAR_THICKNESS,
      categoryPercentage: CATEGORY_WIDTH_SHARE,
    },
  ],
}));

function scales() {
  const colors = chartColors();
  return {
    x: { display: false, beginAtZero: true },
    y: {
      grid: { display: false },
      border: { display: false },
      ticks: {
        color: colors.text,
        padding: Y_TICK_PADDING,
        callback: (tickValue: string | number) => props.data.labels[Number(tickValue)].split(LABEL_SEPARATOR),
      },
    },
  };
}

const summary = computed(() => conversionChartSummary(props.data));

const options = computed(() => ({
  indexAxis: "y" as const,
  responsive: true,
  maintainAspectRatio: false,
  animation: false as const,
  layout: { padding: { right: VALUE_LABEL_SPACE } },
  scales: scales(),
  plugins: {
    legend: { display: false },
    tooltip: {
      ...tooltipStyle(),
      callbacks: {
        label: (item: TooltipItem<"bar">) => `${item.formattedValue}% of ${props.data.calls[item.dataIndex]} calls`,
      },
    },
  },
}));
</script>

<template>
  <Bar :data="chartData" :options="options" :plugins="[valueLabels]" :aria-label="summary" />
</template>
