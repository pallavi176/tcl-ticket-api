"""JWT creation and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings


class TokenPayload(BaseModel):
    """JWT claims we care about."""

    sub: str
    exp: int | None = None


def create_access_token(*, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Issue a signed JWT."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": int(expire.timestamp())}
    if extra_claims:
        to_encode.update(extra_claims)
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """Validate JWT and return payload."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not isinstance(sub, str) or not sub:
            raise JWTError("Invalid subject")
        exp = payload.get("exp")
        exp_int = int(exp) if exp is not None else None
        return TokenPayload(sub=sub, exp=exp_int)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
