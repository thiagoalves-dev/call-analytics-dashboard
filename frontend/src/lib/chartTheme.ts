import { Chart } from "chart.js";

export const CHART_FONT_FAMILY = "Inter, system-ui, -apple-system, sans-serif";

Chart.defaults.font.family = CHART_FONT_FAMILY;
Chart.defaults.font.size = 12;

export interface ChartColors {
  text: string;
  muted: string;
  grid: string;
}

function cssVariable(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function chartColors(): ChartColors {
  return { text: cssVariable("--text"), muted: cssVariable("--muted"), grid: cssVariable("--grid") };
}

export function tooltipStyle() {
  return {
    backgroundColor: "rgba(15, 21, 35, 0.94)",
    titleColor: "#ffffff",
    bodyColor: "#d6dae3",
    titleFont: { weight: 600 as const },
    padding: 10,
    cornerRadius: 8,
    boxPadding: 4,
    usePointStyle: true,
  };
}
