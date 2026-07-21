from __future__ import annotations


class SecretVersionApplicationError(RuntimeError):
    """Base class for SecretVersion application errors."""


class SecretVersionValidationError(SecretVersionApplicationError):
    """Raised when a SecretVersion request violates validation."""


class SecretNotFoundError(SecretVersionApplicationError):
    """Raised when the parent Secret does not exist."""


class SecretVersionNotFoundError(SecretVersionApplicationError):
    """Raised when a requested SecretVersion does not exist."""


class SecretVersionConflictError(SecretVersionApplicationError):
    """Raised when a SecretVersion persistence conflict occurs."""


class SecretVersionCryptoError(SecretVersionApplicationError):
    """Raised when a SecretVersion cannot be encrypted or decrypted safely."""
