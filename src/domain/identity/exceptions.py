from __future__ import annotations


class IdentityDomainError(ValueError):
    """Base class for identity domain validation errors."""


class IdentityValueError(IdentityDomainError):
    """Raised when an identity value object is invalid."""
