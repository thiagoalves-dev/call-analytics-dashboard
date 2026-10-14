from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Granularity(StrEnum):
    HOUR = "hour"
    DAY = "day"

    def is_hourly(self) -> bool:
        return self is Granularity.HOUR


class ConversionGrouping(StrEnum):
    CAMPAIGN = "campaign"
    SOURCE = "source"

    def by_campaign(self) -> bool:
        return self is ConversionGrouping.CAMPAIGN


class VolumePoint(BaseModel):
    bucket: datetime
    total: int
    missed: int
    connected: int
    converted: int


class VolumeResponse(BaseModel):
    granularity: Granularity
    timezone: str
    points: list[VolumePoint]


class ConversionRow(BaseModel):
    key: str
    label: str
    source: str
    calls: int
    missed: int
    connected: int
    converted: int
    conversion_rate: float | None


class ConversionResponse(BaseModel):
    group_by: ConversionGrouping
    rows: list[ConversionRow]
