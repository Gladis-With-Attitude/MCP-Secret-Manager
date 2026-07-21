from __future__ import annotations


class RbacDomainError(ValueError):
    """Base class for RBAC domain validation errors."""


class RbacValueError(RbacDomainError):
    """Raised when an RBAC value object is invalid."""
