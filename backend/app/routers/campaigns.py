from fastapi import APIRouter

from app.dependencies.auth import CurrentPrincipal, IngestAccount
from app.dependencies.database import Session
from app.repositories import campaign_repository
from app.schemas.campaign import CampaignResponse

router = APIRouter(prefix="/api", tags=["campaigns"])


@router.get("/campaigns")
async def list_campaigns(principal: CurrentPrincipal, session: Session) -> list[CampaignResponse]:
    campaigns = await campaign_repository.for_account(session, principal.account_id)
    return [CampaignResponse.model_validate(campaign) for campaign in campaigns]


@router.get("/ingest/tracking-numbers")
async def list_tracking_numbers(account: IngestAccount, session: Session) -> list[str]:
    return list(await campaign_repository.tracking_numbers_for_account(session, account.id))
