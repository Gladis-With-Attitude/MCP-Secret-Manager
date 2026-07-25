from __future__ import annotations


class AuditValidationError(ValueError):
    """Raised when an audit query or event input is invalid."""


class AuditNotFoundError(LookupError):
    """Raised when an audit event does not exist."""
