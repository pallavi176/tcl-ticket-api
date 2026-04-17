"""tblTicketDetails persistence."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.decorators import log_execution, translate_db_errors
from app.models.ticket import TicketDetail
from app.schemas.ticket import TicketCreate, TicketUpdate

DEFAULT_LIST_LIMIT = 100
MAX_LIST_LIMIT = 500


class TicketRepository:
    """Encapsulates SQLAlchemy queries for tickets."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @log_execution(log_args=False)
    @translate_db_errors()
    async def get_by_id(self, ticket_id: int) -> TicketDetail | None:
        """Load one ticket by primary key."""
        result = await self._session.execute(
            select(TicketDetail).where(TicketDetail.ticket_id == ticket_id)
        )
        return result.scalar_one_or_none()

    @log_execution(log_args=False)
    @translate_db_errors()
    async def list_all(self, skip: int = 0, limit: int = DEFAULT_LIST_LIMIT) -> list[TicketDetail]:
        """List tickets (newest first), paginated."""
        cap = min(max(1, limit), MAX_LIST_LIMIT)
        safe_skip = max(0, skip)
        result = await self._session.execute(
            select(TicketDetail)
            .order_by(TicketDetail.created_at.desc())
            .offset(safe_skip)
            .limit(cap)
        )
        return list(result.scalars().all())

    @log_execution(log_args=False)
    @translate_db_errors()
    async def create(self, data: TicketCreate) -> TicketDetail:
        """Insert a row into tblTicketDetails."""
        row = TicketDetail(
            title=data.title.strip(),
            description=data.description,
            status=data.status.strip(),
            priority=data.priority.value,
            assigned_to=data.assigned_to.strip() if data.assigned_to else None,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    @log_execution(log_args=False)
    @translate_db_errors()
    async def update(self, ticket_id: int, data: TicketUpdate) -> TicketDetail | None:
        """Apply partial update; returns None if missing."""
        row = await self.get_by_id(ticket_id)
        if row is None:
            return None
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return row
        if "title" in payload and payload["title"] is not None:
            row.title = str(payload["title"]).strip()
        if "description" in payload:
            row.description = payload["description"]
        if "status" in payload and payload["status"] is not None:
            row.status = str(payload["status"]).strip()
        if "priority" in payload and payload["priority"] is not None:
            row.priority = payload["priority"].value
        if "assigned_to" in payload:
            at = payload["assigned_to"]
            row.assigned_to = at.strip() if isinstance(at, str) and at.strip() else at
        await self._session.flush()
        await self._session.refresh(row)
        return row
