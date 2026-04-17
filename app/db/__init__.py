"""Database package (avoid eager engine import from `app.db`)."""

from app.db.base import Base

__all__ = ["Base"]
