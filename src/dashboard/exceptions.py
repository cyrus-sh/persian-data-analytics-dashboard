"""Application-specific exceptions with safe Persian messages."""

from __future__ import annotations


class DashboardError(Exception):
    """Base exception for user-facing dashboard errors."""

    default_message = "خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class FileValidationError(DashboardError):
    """Raised when an uploaded file is invalid or unsafe."""


class DataProcessingError(DashboardError):
    """Raised when data preparation or analysis fails."""


class ChartBuildError(DashboardError):
    """Raised when an interactive chart cannot be created."""
