from __future__ import annotations


class VaultApplicationError(RuntimeError):
    """Base class for Vault application errors."""


class VaultValidationError(VaultApplicationError):
    """Raised when a create Vault request violates domain validation."""


class VaultAlreadyExistsError(VaultApplicationError):
    """Raised when a Vault with the same name already exists."""


class VaultNotFoundError(VaultApplicationError):
    """Raised when a Vault does not exist."""


class VaultArchivedError(VaultApplicationError):
    """Raised when an operation is not allowed on an archived Vault."""
