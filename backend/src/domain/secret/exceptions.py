from __future__ import annotations


class SecretDomainError(ValueError):
    """Base class for Secret domain invariant violations."""


class SecretKeyError(SecretDomainError):
    """Raised when a secret key violates domain invariants."""
