from __future__ import annotations


class VaultDomainError(ValueError):
    """Base class for Vault domain invariant violations."""


class VaultNameError(VaultDomainError):
    """Raised when a vault name violates domain invariants."""
