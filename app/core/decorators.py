"""Reusable decorators (timing, exception translation)."""

from __future__ import annotations

import functools
import inspect
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, cast

from app.core.exceptions import AppError, ValidationAppError

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def log_execution(
    *,
    level: int = logging.DEBUG,
    log_args: bool = False,
) -> Callable[[F], F]:
    """Log function name, duration, and optional arguments."""

    def decorator(func: F) -> F:
        is_coro = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            if log_args:
                logger.log(level, "Calling %s args=%s kwargs=%s", func.__name__, args, kwargs)
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.log(level, "%s completed in %.2f ms", func.__name__, elapsed_ms)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            if log_args:
                logger.log(level, "Calling %s args=%s kwargs=%s", func.__name__, args, kwargs)
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.log(level, "%s completed in %.2f ms", func.__name__, elapsed_ms)

        return cast(F, async_wrapper if is_coro else sync_wrapper)

    return decorator


def translate_db_errors() -> Callable[[F], F]:
    """Map SQLAlchemy / DB errors to AppError where practical."""

    def decorator(func: F) -> F:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("translate_db_errors applies to async functions only")

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await cast(Callable[..., Awaitable[Any]], func)(*args, **kwargs)
            except AppError:
                raise
            except Exception as exc:  # pylint: disable=broad-exception-caught
                msg = str(exc).lower()
                if "duplicate" in msg or "unique" in msg:
                    raise ValidationAppError(
                        "Duplicate or conflicting record", code="CONFLICT"
                    ) from exc
                logger.exception("Unexpected persistence error in %s", func.__name__)
                raise AppError(
                    "Database operation failed",
                    code="DB_ERROR",
                    status_code=500,
                    details={"original": type(exc).__name__},
                ) from exc

        return cast(F, async_wrapper)

    return decorator
