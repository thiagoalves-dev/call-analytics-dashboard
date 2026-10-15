from fastapi import APIRouter

from app.actions.stats.build_call_volume import BuildCallVolume
from app.actions.stats.build_conversion_report import BuildConversionReport
from app.dependencies.auth import CurrentPrincipal
from app.dependencies.call_filter import CallFilterQuery
from app.dependencies.database import Session
from app.schemas.stats import ConversionGrouping, ConversionResponse, Granularity, VolumeResponse

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/volume")
async def volume(
    principal: CurrentPrincipal,
    session: Session,
    call_filter: CallFilterQuery,
    granularity: Granularity = Granularity.HOUR,
) -> VolumeResponse:
    return await BuildCallVolume(session, principal.account_id, call_filter, granularity)()


@router.get("/conversion")
async def conversion(
    principal: CurrentPrincipal,
    session: Session,
    call_filter: CallFilterQuery,
    group_by: ConversionGrouping = ConversionGrouping.CAMPAIGN,
) -> ConversionResponse:
    return await BuildConversionReport(session, principal.account_id, call_filter, group_by)()
