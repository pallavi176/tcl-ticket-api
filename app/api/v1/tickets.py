"""Ticket CRUD routes (assignment endpoints)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import CurrentUser, get_settings_dep, get_ticket_service
from app.config import Settings, get_settings
from app.core.limiter import limiter
from app.schemas.ticket import TicketCreate, TicketOut, TicketUpdate
from app.services.ticket_service import TicketService

router = APIRouter(tags=["tickets"])


def _rate_limit_write() -> str:
    """POST/PUT ticket limits from env (SlowAPI calls provider with no args)."""
    return get_settings().rate_limit_default


def _rate_limit_read() -> str:
    """GET ticket limits from env (typically higher than writes)."""
    return get_settings().rate_limit_burst


@router.post(
    "",
    response_model=TicketOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ticket",
)
@limiter.limit(_rate_limit_write)
async def create_ticket(
    request: Request,
    _user: CurrentUser,
    body: TicketCreate,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> TicketOut:
    """POST /tickets — insert into tblTicketDetails."""
    _ = request, settings
    return await svc.create_ticket(body)


@router.get(
    "",
    response_model=list[TicketOut],
    summary="List tickets",
)
@limiter.limit(_rate_limit_read)
async def list_tickets(
    request: Request,
    _user: CurrentUser,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
    skip: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
    limit: Annotated[int, Query(ge=1, le=500, description="Page size (max 500)")] = 100,
) -> list[TicketOut]:
    """GET /tickets — list tickets, newest first (paginated)."""
    _ = request
    return await svc.list_tickets(skip=skip, limit=limit)


@router.post(
    "/{ticket_id}/close",
    response_model=TicketOut,
    summary="Close ticket",
)
@limiter.limit(_rate_limit_write)
async def close_ticket(
    request: Request,
    ticket_id: int,
    _user: CurrentUser,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketOut:
    """POST /tickets/{id}/close — set status to `closed` (lifecycle)."""
    _ = request
    return await svc.close_ticket(ticket_id)


@router.get(
    "/{ticket_id}",
    response_model=TicketOut,
    summary="Get ticket details",
)
@limiter.limit(_rate_limit_read)
async def get_ticket(
    request: Request,
    ticket_id: int,
    _user: CurrentUser,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketOut:
    """GET /tickets/{id}."""
    _ = request
    return await svc.get_ticket(ticket_id)


@router.put(
    "/{ticket_id}",
    response_model=TicketOut,
    summary="Update ticket",
)
@limiter.limit(_rate_limit_write)
async def update_ticket(
    request: Request,
    ticket_id: int,
    _user: CurrentUser,
    body: TicketUpdate,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketOut:
    """PUT /tickets/{id} — partial update supported."""
    _ = request
    return await svc.update_ticket(ticket_id, body)


@router.patch(
    "/{ticket_id}",
    response_model=TicketOut,
    summary="Patch ticket (partial update)",
)
@limiter.limit(_rate_limit_write)
async def patch_ticket(
    request: Request,
    ticket_id: int,
    _user: CurrentUser,
    body: TicketUpdate,
    svc: Annotated[TicketService, Depends(get_ticket_service)],
) -> TicketOut:
    """PATCH /tickets/{id} — same as PUT: update one or more fields."""
    _ = request
    return await svc.update_ticket(ticket_id, body)
