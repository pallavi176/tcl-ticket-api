"""tblTicketDetails ORM mapping."""

from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Priority(str, PyEnum):
    """Ticket priority (matches DB ENUM values)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TicketDetail(Base):
    """Maps to TestDB.tblTicketDetails."""

    __tablename__ = "tblTicketDetails"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    # MySQL ENUM stored as string for reliable async driver compatibility
    priority: Mapped[str] = mapped_column(
        String(16), nullable=False, server_default=text("'MEDIUM'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
