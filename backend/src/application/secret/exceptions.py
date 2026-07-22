from __future__ import annotations


class SecretApplicationError(RuntimeError):
    """Base class for Secret application errors."""


class SecretValidationError(SecretApplicationError):
    """Raised when a create Secret request violates validation."""


class ProjectNotFoundError(SecretApplicationError):
    """Raised when the parent Project does not exist."""


class ProjectArchivedError(SecretApplicationError):
    """Raised when creating a Secret in an archived Project is forbidden."""


class SecretAlreadyExistsError(SecretApplicationError):
    """Raised when a Secret key already exists in a Project."""


class SecretNotFoundError(SecretApplicationError):
    """Raised when a Secret does not exist in the expected Project."""


class SecretArchivedError(SecretApplicationError):
    """Raised when mutating an archived Secret is forbidden."""
