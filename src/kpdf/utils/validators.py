"""Validation helpers shared by UI and operations."""

from pathlib import Path


class ValidationError(ValueError):
    """Raised when user inputs fail validation."""


def require_existing_file(path: str) -> Path:
    candidate = Path(path)
    if not candidate.exists() or not candidate.is_file():
        raise ValidationError(f"File does not exist: {path}")
    return candidate


def require_existing_directory(path: str) -> Path:
    candidate = Path(path)
    if not candidate.exists() or not candidate.is_dir():
        raise ValidationError(f"Directory does not exist: {path}")
    return candidate
