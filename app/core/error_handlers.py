"""Map exceptions to structured JSON responses."""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError
from app.core.request_context import get_request_id
from app.schemas.common import ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


def _error_body(
    *,
    code: str,
    message: str,
    status_code: int,
    field: str | None = None,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorDetail(code=code, message=message, field=field),
        request_id=get_request_id(),
        details=details,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Domain errors."""
    return _error_body(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        field=exc.field,
        details=exc.details,
    )


async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    """Pydantic / FastAPI request validation (422)."""
    errs = exc.errors()
    first = errs[0] if errs else {}
    loc = first.get("loc", ())
    field = ".".join(str(x) for x in loc if x != "body") or None
    message = first.get("msg", "Invalid request")
    return _error_body(
        code="INVALID_REQUEST",
        message=str(message),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        field=field,
        details={"errors": errs},
    )


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Starlette/FastAPI HTTP errors with unified envelope."""
    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code", "HTTP_ERROR"))
        message = str(detail.get("message", detail))
    else:
        code = "HTTP_ERROR"
        message = str(detail)
    return _error_body(
        code=code,
        message=message,
        status_code=exc.status_code,
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Unexpected errors (500) with correlation id; log stack trace."""
    logger.exception("Unhandled error: %s", exc)
    return _error_body(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"type": type(exc).__name__},
    )
