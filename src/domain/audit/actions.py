from __future__ import annotations

AUDIT_ACTIONS: tuple[str, ...] = (
    "vault.create",
    "vault.update",
    "vault.delete",
    "project.create",
    "secret.create",
    "secret.read",
    "secret.decrypt",
    "secret.rotate",
    "secret.delete",
    "apikey.create",
    "apikey.revoke",
    "login.success",
    "login.failure",
    "permission.denied",
)
