from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequirePermission:
    identity_id: str
    identity_type: str
    permission: str
    scope_type: str
    scope_id: str | None = None
    parent_vault_id: str | None = None
    parent_project_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    allowed: bool
