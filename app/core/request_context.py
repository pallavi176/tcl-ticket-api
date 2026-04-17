"""Request correlation id (middleware sets, handlers read)."""

import contextvars
import uuid

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)


def get_request_id() -> str:
    """Return current request id or generate one."""
    rid = request_id_ctx.get()
    if rid is None:
        rid = str(uuid.uuid4())
        request_id_ctx.set(rid)
    return rid


def set_request_id(request_id: str | None) -> contextvars.Token[str | None]:
    """Bind request id for this async context."""
    return request_id_ctx.set(request_id)
