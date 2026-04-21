"""Error classes and conversion for user-safe messages."""

from dataclasses import dataclass


class KPDFError(Exception):
    """Base error for all application-level failures."""


class OperationError(KPDFError):
    """Raised when an operation fails."""


@dataclass(slots=True)
class UserError:
    title: str
    message: str


def to_user_error(exc: Exception) -> UserError:
    if isinstance(exc, OperationError):
        return UserError(title="Operation Failed", message=str(exc))
    if isinstance(exc, KPDFError):
        return UserError(title="kPDF Error", message=str(exc))
    return UserError(title="Unexpected Error", message="An unexpected error occurred.")
