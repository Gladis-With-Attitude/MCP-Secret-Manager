# Rotation Strategy

This document defines the current operational rotation strategy for production
readiness. It covers application secrets, stored secret values, PostgreSQL
credentials, backup access credentials and the application master key in the
context of the D5 backup and recovery tooling.

## Scope

Rotation is an operational change, not only a cryptographic change. Every
planned rotation must identify:

- the credential or key being replaced;
- the owner approving the change;
- the recovery point created before the change;
- the validation checks required before traffic returns;
- the rollback path if validation fails.

The current runtime supports one active `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`
and one `MCP_SECRET_MANAGER_MASTER_KEY_VERSION` at a time. Historical secret
versions are decryptable only when the configured master key and key version
match the values used to wrap their data encryption keys. Do not replace the
master key in place and expect old encrypted versions to remain readable.

## Rotation Inventory

| Item | Trigger | Strategy | Recovery Link |
| --- | --- | --- | --- |
| Stored business secret values | Routine credential expiry, downstream compromise, owner request | Create a new `SecretVersion` through the normal `secret.rotate` workflow. Do not overwrite older versions. | Take or identify a recent PostgreSQL backup first for high-risk bulk rotations. |
| MCP Secret Manager API keys | Owner offboarding, permission change, suspected exposure | Create a replacement API key, update consumers, verify authentication, then revoke the old key. | Raw keys are not recoverable from PostgreSQL; keep bootstrap or break-glass keys in a separate approved channel. |
| Runtime signing secret `MCP_SECRET_MANAGER_SECRET_KEY` | Suspected session/signing exposure, planned security refresh | Generate a new production secret, deploy during a maintenance window and expect existing signed state to be invalidated. | Keep the previous value only in the approved rollback channel until post-rotation validation passes. |
| Application master key `MCP_SECRET_MANAGER_MASTER_KEY_BASE64` | Confirmed or likely master-key exposure, cryptographic migration | Treat as a break-glass migration. See "Master Key Replacement". | Requires the pre-rotation PostgreSQL dump and the old master key for rollback or historical decryption. |
| PostgreSQL credentials | Database access exposure, hosting credential rotation | Create replacement database credentials, update `MCP_SECRET_MANAGER_DATABASE_URL`, run readiness checks and retire the old credential. | Verify `make db-backup` works after the change so the backup channel is still usable. |
| Backup storage credentials | Backup location exposure, operator offboarding | Move future dumps to the new restricted location or credential, verify checksum access and retire old access. | Existing dumps remain sensitive; preserve retention and access logs for incident review. |

## Planned Rotation Procedure

Use this flow for routine rotations and maintenance-window credential refreshes:

1. Confirm scope, owner, target environment and rollback decision owner.
2. Run or select a current PostgreSQL backup and verify its checksum:

```bash
make db-backup BACKUP_DIR=/secure/operator/backups/postgres
sha256sum -c /secure/operator/backups/postgres/<dump>.sha256
```

3. Confirm the relevant runtime secrets are recoverable from the separate
   approved channel. Never store the master key beside PostgreSQL dumps.
4. Drain traffic or pause writers when rotating infrastructure credentials or
   when a bulk stored-secret rotation could leave consumers inconsistent.
5. Apply the rotation through the smallest supported workflow:
   `secret.rotate` for stored values, replacement then revocation for API keys,
   configuration deployment for runtime credentials.
6. Validate the result before returning traffic:
   `make deployment-readiness DEPLOYMENT_ENV_FILE=<env-file>`, `make db-current`,
   `GET /v1/health`, authentication with the replacement credential and one
   representative secret decrypt.
7. Record the rotation in the operational log with timestamp, owner, affected
   items, backup checksum status and validation result. Do not record secret
   values, raw API keys or master keys.

## Master Key Replacement

Master-key replacement is not routine rotation in the current implementation.
Because the runtime accepts one active master key and key version, existing
encrypted versions cannot be transparently read after replacing
`MCP_SECRET_MANAGER_MASTER_KEY_BASE64`.

Use this break-glass path only for confirmed or likely master-key compromise:

1. Preserve availability first when needed by restoring with the existing
   PostgreSQL dump and the old master key through `backend/docs/DISASTER_RECOVERY.md`.
2. Assume stored secret values are compromised if the dump and old master key may
   both have been exposed.
3. Generate a new 32-byte master key and increment
   `MCP_SECRET_MANAGER_MASTER_KEY_VERSION` for the target environment.
4. During a maintenance window, deploy the new key and create fresh active
   secret versions from the authoritative downstream owners or systems.
5. Verify that active versions decrypt under the new key. Historical versions
   encrypted under the old key are available only through a separately restored
   environment configured with the old key.
6. Keep the old key only in the approved recovery channel for the retention
   window required by audit and incident response, then destroy it according to
   policy.

If validation fails after a master-key replacement, restore the pre-rotation
PostgreSQL dump and the old runtime configuration together. Restoring only one
side is not sufficient.

## Incident Rotation

When exposure is suspected, choose the rotation set by blast radius:

- API key exposure: create a replacement key, update consumers, revoke the old
  key and review audit events for the exposed prefix.
- PostgreSQL dump exposure without master-key exposure: rotate backup storage
  access and database credentials; review metadata exposure; keep the master key
  isolated.
- Dump plus master-key exposure: follow master-key replacement and rotate every
  stored downstream credential because encrypted values may be compromised.
- Runtime host or container compromise: rotate runtime signing secret,
  PostgreSQL credentials, API keys used by that host and any stored secrets that
  were decrypted or could have been accessed.

After incident rotation, run the post-restore validation checklist from
`backend/docs/DISASTER_RECOVERY.md` when a restore was involved, and keep traffic
drained until decryption, authentication and audit checks pass.
