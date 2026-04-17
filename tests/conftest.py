"""Pytest fixtures: in-memory SQLite app, auth disabled."""

from __future__ import annotations

import os

# Must run before any `app` import so `get_settings()` / engine see test configuration.
os.environ["ENABLE_AUTH"] = "false"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from collections.abc import AsyncGenerator  # noqa: E402

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app

get_settings.cache_clear()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client against app with overridden async DB session."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app = create_app()
    app.dependency_overrides[get_db_session] = override_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await engine.dispose()
    app.dependency_overrides.clear()
