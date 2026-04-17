"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.services.ticket_service import TicketService

security_scheme = HTTPBearer(auto_error=False)


async def get_settings_dep() -> Settings:
    """Inject cached Settings."""
    return get_settings()


async def get_ticket_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TicketService:
    """Inject TicketService with request-scoped DB session."""
    return TicketService(session)


async def require_user(
    settings: Annotated[Settings, Depends(get_settings_dep)],
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> str:
    """JWT bearer auth when enable_auth is True; otherwise anonymous 'dev' subject."""
    if not settings.enable_auth:
        return "dev"
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "UNAUTHORIZED", "message": "Missing bearer token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(creds.credentials)
        return payload.sub
    except ValueError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


CurrentUser = Annotated[str, Depends(require_user)]
