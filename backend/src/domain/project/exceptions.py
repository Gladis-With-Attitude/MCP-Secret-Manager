from __future__ import annotations


class ProjectDomainError(ValueError):
    """Base class for Project domain invariant violations."""


class ProjectNameError(ProjectDomainError):
    """Raised when a project name violates domain invariants."""
