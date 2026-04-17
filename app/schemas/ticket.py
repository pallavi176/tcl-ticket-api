"""Ticket request/response schemas."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Priority(str, Enum):
    """API priority values (aligned with tblTicketDetails.priority)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TicketCreate(BaseModel):
    """POST /tickets body."""

    title: str = Field(..., min_length=1, max_length=512)
    description: str | None = Field(None, max_length=65535)
    status: str = Field(..., min_length=1, max_length=255)
    priority: Priority = Priority.MEDIUM
    assigned_to: str | None = Field(None, max_length=255)


class TicketUpdate(BaseModel):
    """PUT or PATCH /tickets/{id} body (partial update; send only fields to change)."""

    title: str | None = Field(None, min_length=1, max_length=512)
    description: str | None = Field(None, max_length=65535)
    status: str | None = Field(None, min_length=1, max_length=255)
    priority: Priority | None = None
    assigned_to: str | None = Field(None, max_length=255)

    @field_validator("title", "description", "status", "assigned_to", mode="before")
    @classmethod
    def strip_strings(cls, v: str | None) -> str | None:
        """Trim whitespace; empty string becomes None for optional fields."""
        if isinstance(v, str):
            s = v.strip()
            return s if s else None
        return v


class TicketOut(BaseModel):
    """Ticket representation returned by APIs."""

    model_config = ConfigDict(from_attributes=True)

    ticket_id: int
    title: str
    description: str | None
    status: str
    priority: Priority
    created_at: datetime
    updated_at: datetime
    assigned_to: str | None

    @field_validator("priority", mode="before")
    @classmethod
    def coerce_priority(cls, v: str | Priority) -> Priority:
        """Accept ORM string or enum for priority."""
        if isinstance(v, Priority):
            return v
        return Priority(v)
