import type { CallStatus, ConversionRow, VolumeResponse } from "../api/types";
import { formatBucket, formatCount } from "./format";
import { ALL_STATUSES } from "./filters";
import { STATUS_COLORS, STATUS_LABELS } from "./statusColors";

const TENTHS_OF_A_PERCENT_PER_UNIT = 1000;
const TENTHS_PER_PERCENT = 10;

export interface StatusSeries {
  status: CallStatus;
  label: string;
  color: string;
  values: number[];
}

export interface VolumeChartData {
  labels: string[];
  series: StatusSeries[];
}

export interface ConversionChartData {
  labels: string[];
  ratesInPercent: number[];
  calls: number[];
}

export function volumeChartData(volume: VolumeResponse): VolumeChartData {
  return {
    labels: volume.points.map((point) => formatBucket(point.bucket, volume.granularity, volume.timezone)),
    series: ALL_STATUSES.map((status) => ({
      status,
      label: STATUS_LABELS[status],
      color: STATUS_COLORS[status],
      values: volume.points.map((point) => point[status]),
    })),
  };
}

export function conversionChartData(rows: ConversionRow[]): ConversionChartData {
  return {
    labels: rows.map((row) => row.label),
    ratesInPercent: rows.map((row) => toRoundedPercent(row.conversion_rate)),
    calls: rows.map((row) => row.calls),
  };
}

export function toRoundedPercent(rate: number | null): number {
  return Math.round((rate ?? 0) * TENTHS_OF_A_PERCENT_PER_UNIT) / TENTHS_PER_PERCENT;
}

export function volumeChartSummary(data: VolumeChartData): string {
  const totals = data.series.map((series) => `${formatCount(sum(series.values))} ${series.label.toLowerCase()}`);
  return `Call volume across ${data.labels.length} periods: ${totals.join(", ")}.`;
}

export function conversionChartSummary(data: ConversionChartData): string {
  const rates = data.labels.map((label, index) => `${label} ${data.ratesInPercent[index]}%`);
  return `Conversion rate: ${rates.join(", ") || "no calls"}.`;
}

function sum(values: number[]): number {
  return values.reduce((total, value) => total + value, 0);
}
