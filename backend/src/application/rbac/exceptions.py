from __future__ import annotations


class RbacApplicationError(RuntimeError):
    """Base class for RBAC application errors."""


class RbacValidationError(RbacApplicationError):
    """Raised when an authorization request is invalid."""


class RbacNotFoundError(RbacApplicationError):
    """Raised when an RBAC resource does not exist."""


class RbacConflictError(RbacApplicationError):
    """Raised when an RBAC mutation conflicts with existing state."""


class AuthorizationDeniedError(RbacApplicationError):
    """Raised when an authenticated identity lacks a required permission."""
