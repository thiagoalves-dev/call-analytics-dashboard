import type { ConversionRow } from "../api/types";

export interface KpiTotals {
  calls: number;
  missed: number;
  converted: number;
}

export function sumConversionRows(rows: ConversionRow[]): KpiTotals {
  return rows.reduce(
    (sum, row) => ({
      calls: sum.calls + row.calls,
      missed: sum.missed + row.missed,
      converted: sum.converted + row.converted,
    }),
    { calls: 0, missed: 0, converted: 0 },
  );
}

export function shareOfCalls(part: number, totals: KpiTotals): number | null {
  return totals.calls ? part / totals.calls : null;
}
