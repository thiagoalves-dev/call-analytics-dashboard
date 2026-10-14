import type { CallStatus, ConversionRow, VolumeResponse } from "../api/types";
import { formatBucket } from "./format";
import { ALL_STATUSES } from "./filters";
import { STATUS_COLORS, STATUS_LABELS } from "./statusColors";

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
    ratesInPercent: rows.map((row) => Math.round((row.conversion_rate ?? 0) * 1000) / 10),
    calls: rows.map((row) => row.calls),
  };
}
