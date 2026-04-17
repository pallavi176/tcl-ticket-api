"""FastAPI application factory and HTTP server entry."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import auth as auth_router
from app.api.v1 import tickets as tickets_router
from app.config import get_settings
from app.core.error_handlers import (
    app_error_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.exceptions import AppError
from app.core.limiter import limiter
from app.core.logging_config import setup_logging
from app.db.session import engine
from app.middleware.request_id import RequestIdMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown hooks."""
    setup_logging()
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory (tests import this)."""
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=(
            "Ticket management API backed by MySQL `TestDB.tblTicketDetails`. "
            "Includes JWT authentication (demo user), rate limiting (SlowAPI), "
            "structured JSON errors, and request correlation via `X-Request-ID`."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    application.add_middleware(RequestIdMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)

    @application.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        """Load balancer / k8s probe."""
        return {"status": "ok"}

    @application.get("/", tags=["health"])
    async def root() -> dict[str, str]:
        """Browser root; Railway health checks often hit `/`."""
        return {"service": settings.app_name, "docs": "/docs", "health": "/health"}

    application.include_router(auth_router.router, prefix="")
    application.include_router(tickets_router.router, prefix="/tickets")

    return application


app = create_app()
