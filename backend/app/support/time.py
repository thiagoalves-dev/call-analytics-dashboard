from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo


def start_of_hour(moment: datetime) -> datetime:
    return moment.astimezone(UTC).replace(minute=0, second=0, microsecond=0)


def local_midnight(day: date, timezone: str) -> datetime:
    return datetime.combine(day, time.min, tzinfo=ZoneInfo(timezone))


def local_date(moment: datetime, timezone: str) -> date:
    return moment.astimezone(ZoneInfo(timezone)).date()
