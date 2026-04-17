"""Shared API models."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Single error item."""

    code: str = Field(..., description="Stable machine-readable code")
    message: str = Field(..., description="Human-readable message")
    field: str | None = Field(None, description="Request field, if applicable")


class ErrorResponse(BaseModel):
    """Structured JSON error envelope."""

    success: bool = False
    error: ErrorDetail
    request_id: str | None = None
    details: dict[str, Any] | None = None
