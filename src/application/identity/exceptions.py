from __future__ import annotations


class IdentityApplicationError(RuntimeError):
    """Base class for identity application errors."""


class IdentityValidationError(IdentityApplicationError):
    """Raised when an identity request violates validation rules."""


class IdentityConflictError(IdentityApplicationError):
    """Raised when an identity resource already exists."""


class IdentityNotFoundError(IdentityApplicationError):
    """Raised when an identity owner or parent resource does not exist."""


class AuthenticationFailedError(IdentityApplicationError):
    """Raised when authentication material is invalid or no longer usable."""
