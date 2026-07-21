from __future__ import annotations


class AuditDomainError(ValueError):
    """Base class for audit domain validation errors."""


class AuditValueError(AuditDomainError):
    """Raised when an audit value object is invalid."""
