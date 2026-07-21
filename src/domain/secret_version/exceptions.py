from __future__ import annotations


class SecretVersionDomainError(ValueError):
    """Base class for SecretVersion domain invariant violations."""


class SecretValueError(SecretVersionDomainError):
    """Raised when a secret value violates domain invariants."""


class SecretVersionNumberError(SecretVersionDomainError):
    """Raised when a secret version number violates domain invariants."""
