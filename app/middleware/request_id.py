"""Attach X-Request-ID for tracing."""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import request_id_ctx


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Propagate or generate X-Request-ID."""

    header_name = "X-Request-ID"

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        incoming = request.headers.get(self.header_name)
        rid = incoming or str(uuid.uuid4())
        token = request_id_ctx.set(rid)
        try:
            response: Response = await call_next(request)
            response.headers[self.header_name] = rid
            return response
        finally:
            request_id_ctx.reset(token)
