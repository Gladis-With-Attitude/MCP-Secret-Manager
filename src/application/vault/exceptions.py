from __future__ import annotations


class VaultApplicationError(RuntimeError):
    """Base class for Vault application errors."""


class VaultValidationError(VaultApplicationError):
    """Raised when a create Vault request violates domain validation."""


class VaultAlreadyExistsError(VaultApplicationError):
    """Raised when a Vault with the same name already exists."""
