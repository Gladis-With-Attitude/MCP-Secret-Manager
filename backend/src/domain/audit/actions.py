from __future__ import annotations

AUDIT_ACTIONS: tuple[str, ...] = (
    "vault.create",
    "vault.read",
    "vault.update",
    "vault.archive",
    "vault.delete",
    "project.create",
    "project.read",
    "project.update",
    "project.archive",
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
