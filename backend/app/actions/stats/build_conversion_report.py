from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.actions.stats.bucketing import HourlyBucketing
from app.models import Campaign
from app.repositories import call_stats_repository
from app.schemas.call_filter import CallFilter
from app.schemas.stats import ConversionGrouping, ConversionResponse, ConversionRow


class BuildConversionReport:
    def __init__(
        self, session: AsyncSession, account_id: int, call_filter: CallFilter, group_by: ConversionGrouping
    ) -> None:
        self.session = session
        self.account_id = account_id
        self.call_filter = call_filter
        self.group_by = group_by

    async def __call__(self) -> ConversionResponse:
        whole_hours = HourlyBucketing().covering(self.call_filter)
        rows = await call_stats_repository.conversion_by(
            self.session, self.account_id, whole_hours, self.group_column()
        )
        report = sorted((self.report_row(row) for row in rows), key=lambda report_row: report_row.calls, reverse=True)
        return ConversionResponse(group_by=self.group_by, rows=report)

    def group_column(self) -> InstrumentedAttribute:
        return Campaign.id if self.group_by.by_campaign() else Campaign.source

    def report_row(self, row: Row) -> ConversionRow:
        return ConversionRow(
            key=str(row.key),
            label=row.campaign_name if self.group_by.by_campaign() else row.source,
            source=row.source,
            calls=row.calls,
            missed=row.missed,
            connected=row.connected,
            converted=row.converted,
            conversion_rate=row.converted / row.calls if row.calls else None,
        )
