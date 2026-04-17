"""Async engine and session factory."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

_settings = get_settings()

_pool_kwargs: dict[str, Any] = {"echo": _settings.debug, "pool_pre_ping": True}
if "sqlite" not in _settings.database_url:
    _pool_kwargs["pool_size"] = 10
    _pool_kwargs["max_overflow"] = 20

engine = create_async_engine(
    _settings.database_url,
    **_pool_kwargs,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: one session per request."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
