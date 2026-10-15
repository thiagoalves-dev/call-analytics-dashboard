import { BarElement, CategoryScale, Chart, LinearScale, Tooltip } from "chart.js";

export const CHART_FONT_FAMILY = "Inter, system-ui, -apple-system, sans-serif";
const CHART_FONT_SIZE = 12;
const TOOLTIP_TITLE_WEIGHT = 600;
const TOOLTIP_PADDING = 10;
const TOOLTIP_CORNER_RADIUS = 8;
const TOOLTIP_SWATCH_GAP = 4;

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip);
Chart.defaults.font.family = CHART_FONT_FAMILY;
Chart.defaults.font.size = CHART_FONT_SIZE;

interface ChartColors {
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
    titleFont: { weight: TOOLTIP_TITLE_WEIGHT },
    padding: TOOLTIP_PADDING,
    cornerRadius: TOOLTIP_CORNER_RADIUS,
    boxPadding: TOOLTIP_SWATCH_GAP,
    usePointStyle: true,
  };
}
