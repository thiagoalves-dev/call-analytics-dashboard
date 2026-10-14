from typing import Annotated

from fastapi import APIRouter, Query, Request, Response, status
from fastapi.responses import StreamingResponse

from app.actions.calls.store_call import StoreCall
from app.dependencies.auth import CurrentPrincipal, IngestAccount
from app.dependencies.call_filter import CallFilterQuery
from app.dependencies.database import Session
from app.repositories import call_repository
from app.schemas.call import CallResponse, StoreCallRequest
from app.services.live_feed import call_events

router = APIRouter(prefix="/api", tags=["calls"])

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


@router.post("/calls", status_code=status.HTTP_201_CREATED)
async def store_call(
    body: StoreCallRequest, account: IngestAccount, session: Session, request: Request, response: Response
) -> CallResponse:
    stored = await StoreCall(session, account, body)()
    if stored.created:
        await request.app.state.broadcaster.publish(account.id, stored.call.model_dump_json())
    else:
        response.status_code = status.HTTP_200_OK
    return stored.call


@router.get("/calls")
async def list_calls(
    principal: CurrentPrincipal,
    session: Session,
    call_filter: CallFilterQuery,
    limit: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
) -> list[CallResponse]:
    rows = await call_repository.most_recent(session, principal.account_id, call_filter, limit)
    return [CallResponse.from_models(call, campaign) for call, campaign in rows]


@router.get("/calls/stream", response_class=StreamingResponse)
async def stream_calls(principal: CurrentPrincipal, request: Request) -> StreamingResponse:
    return StreamingResponse(
        call_events(request.app.state.broadcaster, principal.account_id, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
