"""Application-specific exceptions (mapped to HTTP responses)."""


class AppError(Exception):
    """Base for domain errors."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        message: str,
        *,
        code: str = "APP_ERROR",
        status_code: int = 500,
        field: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.field = field
        self.details = details


class ValidationAppError(AppError):
    """Invalid input / business rule violation (400)."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "VALIDATION_ERROR",
        field: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message,
            code=code,
            status_code=400,
            field=field,
            details=details,
        )


class NotFoundError(AppError):
    """Resource missing (404)."""

    def __init__(self, message: str = "Resource not found", *, code: str = "NOT_FOUND") -> None:
        super().__init__(message, code=code, status_code=404)


class UnauthorizedError(AppError):
    """Auth failure (401)."""

    def __init__(self, message: str = "Not authenticated", *, code: str = "UNAUTHORIZED") -> None:
        super().__init__(message, code=code, status_code=401)


class ForbiddenError(AppError):
    """Authorization failure (403)."""

    def __init__(self, message: str = "Forbidden", *, code: str = "FORBIDDEN") -> None:
        super().__init__(message, code=code, status_code=403)
