const PERCENT = new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 });
const COUNT = new Intl.NumberFormat("en-US");
const COMPACT = new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 });

const SECONDS_PER_MINUTE = 60;
const SECONDS_DIGITS = 2;
const INITIALS_LENGTH = 2;
const US_NUMBER_DIGITS = 10;
const AREA_CODE_END = 3;
const EXCHANGE_END = 6;

export function formatPercent(rate: number | null): string {
  return rate === null ? "—" : PERCENT.format(rate);
}

export function formatCount(count: number): string {
  return COUNT.format(count);
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / SECONDS_PER_MINUTE);
  const remainingSeconds = String(seconds % SECONDS_PER_MINUTE).padStart(SECONDS_DIGITS, "0");
  return `${minutes}:${remainingSeconds}`;
}

export function formatBucket(bucket: string, granularity: "hour" | "day", timezone: string): string {
  const options: Intl.DateTimeFormatOptions =
    granularity === "hour"
      ? { month: "short", day: "numeric", hour: "numeric", timeZone: timezone }
      : { month: "short", day: "numeric", weekday: "short", timeZone: timezone };
  return new Intl.DateTimeFormat("en-US", options).format(new Date(bucket));
}

export function formatCompact(count: number): string {
  return COMPACT.format(count);
}

function calendarDay(date: Date, timezone: string): string {
  return new Intl.DateTimeFormat("en-US", { dateStyle: "short", timeZone: timezone }).format(date);
}

export function formatCallTime(endedAt: string, timezone: string, now: Date = new Date()): string {
  const ended = new Date(endedAt);
  const time: Intl.DateTimeFormatOptions = {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    timeZone: timezone,
  };
  const endedToday = calendarDay(ended, timezone) === calendarDay(now, timezone);
  const options: Intl.DateTimeFormatOptions = endedToday ? time : { ...time, month: "short", day: "numeric" };
  return new Intl.DateTimeFormat("en-US", options).format(ended);
}

export function initialsOf(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, INITIALS_LENGTH)
    .map((word) => word[0].toUpperCase())
    .join("");
}

export function formatPhone(number: string): string {
  const digits = number.replace(/^\+1/, "");
  if (digits.length !== US_NUMBER_DIGITS) return number;
  const areaCode = digits.slice(0, AREA_CODE_END);
  return `(${areaCode}) ${digits.slice(AREA_CODE_END, EXCHANGE_END)}-${digits.slice(EXCHANGE_END)}`;
}
