from __future__ import annotations


class SecretApplicationError(RuntimeError):
    """Base class for Secret application errors."""


class SecretValidationError(SecretApplicationError):
    """Raised when a create Secret request violates validation."""


class ProjectNotFoundError(SecretApplicationError):
    """Raised when the parent Project does not exist."""


class SecretAlreadyExistsError(SecretApplicationError):
    """Raised when a Secret key already exists in a Project."""
