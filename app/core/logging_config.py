"""Structured logging setup."""

import logging
import sys
from typing import Any

from app.config import get_settings


def setup_logging() -> None:
    """Configure root logger (JSON or plain text)."""
    settings = get_settings()
    level = getattr(logging, settings.log_level)

    if settings.log_json:

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                payload: dict[str, Any] = {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                }
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                return str(payload).replace("'", '"')  # minimal; use orjson in prod

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    # Quiet noisy libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
