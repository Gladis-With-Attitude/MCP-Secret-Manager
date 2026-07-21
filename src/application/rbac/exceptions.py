from __future__ import annotations


class RbacApplicationError(RuntimeError):
    """Base class for RBAC application errors."""


class RbacValidationError(RbacApplicationError):
    """Raised when an authorization request is invalid."""


class AuthorizationDeniedError(RbacApplicationError):
    """Raised when an authenticated identity lacks a required permission."""
