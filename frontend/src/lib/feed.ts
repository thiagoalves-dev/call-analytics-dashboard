import type { Call } from "../api/types";

export const FEED_SIZE = 50;

const newestFirst = (first: Call, second: Call) => Date.parse(second.ended_at) - Date.parse(first.ended_at);

export function mergeNewest(incoming: Call[], current: Call[]): Call[] {
  const unique = new Map([...current, ...incoming].map((call) => [call.id, call]));
  return [...unique.values()].sort(newestFirst).slice(0, FEED_SIZE);
}
