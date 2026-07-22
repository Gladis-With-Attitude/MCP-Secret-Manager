from __future__ import annotations


class SecretDomainError(ValueError):
    """Base class for Secret domain invariant violations."""


class SecretKeyError(SecretDomainError):
    """Raised when a secret key violates domain invariants."""


class SecretDescriptionError(SecretDomainError):
    """Raised when a secret description violates domain invariants."""


class SecretMetadataError(SecretDomainError):
    """Raised when secret metadata violates domain invariants."""


class SecretTagError(SecretDomainError):
    """Raised when secret tags violate domain invariants."""


class SecretTypeError(SecretDomainError):
    """Raised when a secret type violates domain invariants."""
