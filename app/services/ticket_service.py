"""Ticket use-cases."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import log_execution
from app.core.exceptions import NotFoundError, ValidationAppError
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketOut, TicketUpdate


class TicketService:
    """Coordinates validation rules and persistence for tickets."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = TicketRepository(session)

    @log_execution(log_args=False)
    async def create_ticket(self, data: TicketCreate) -> TicketOut:
        """Create ticket; returns API model."""
        if not data.title or not data.title.strip():
            raise ValidationAppError("title is required", field="title")
        if not data.status or not data.status.strip():
            raise ValidationAppError("status is required", field="status")
        row = await self._repo.create(data)
        return TicketOut.model_validate(row)

    @log_execution(log_args=False)
    async def get_ticket(self, ticket_id: int) -> TicketOut:
        """Fetch ticket or 404."""
        row = await self._repo.get_by_id(ticket_id)
        if row is None:
            raise NotFoundError(f"Ticket {ticket_id} not found", code="TICKET_NOT_FOUND")
        return TicketOut.model_validate(row)

    @log_execution(log_args=False)
    async def list_tickets(self, skip: int = 0, limit: int = 100) -> list[TicketOut]:
        """List tickets (paginated), newest first."""
        rows = await self._repo.list_all(skip=skip, limit=limit)
        return [TicketOut.model_validate(r) for r in rows]

    @log_execution(log_args=False)
    async def close_ticket(self, ticket_id: int) -> TicketOut:
        """Set status to closed (terminal lifecycle step)."""
        return await self.update_ticket(ticket_id, TicketUpdate(status="closed"))

    @log_execution(log_args=False)
    async def update_ticket(self, ticket_id: int, data: TicketUpdate) -> TicketOut:
        """Update ticket; 404 if missing; 400 if no fields."""
        if not data.model_dump(exclude_unset=True):
            raise ValidationAppError(
                "At least one field must be provided for update",
                code="EMPTY_UPDATE",
            )
        row = await self._repo.update(ticket_id, data)
        if row is None:
            raise NotFoundError(f"Ticket {ticket_id} not found", code="TICKET_NOT_FOUND")
        return TicketOut.model_validate(row)
