from __future__ import annotations


class ProjectApplicationError(RuntimeError):
    """Base class for Project application errors."""


class ProjectValidationError(ProjectApplicationError):
    """Raised when a Project request violates validation."""


class VaultNotFoundError(ProjectApplicationError):
    """Raised when the parent Vault does not exist."""


class ProjectNotFoundError(ProjectApplicationError):
    """Raised when a Project does not exist."""


class ProjectAlreadyExistsError(ProjectApplicationError):
    """Raised when a Project with the same name already exists in a Vault."""


class ProjectArchivedError(ProjectApplicationError):
    """Raised when an operation is not allowed on an archived Project."""
