# Backup Guide

This guide is the operator-facing backup entry point for MCP Secret Manager. It
summarizes the D5 PostgreSQL backup tooling and links to the deeper recovery
runbooks when a restore, incident or rotation is involved.

## Scope

The supported backup artifact is a PostgreSQL custom-format dump created from
the Compose `postgres` service, plus a sibling `sha256` checksum file.

The dump contains:

- vault, project, secret and audit metadata;
- encrypted secret values and version history;
- hashed API key material and identity records.

The dump does not contain:

- `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`;
- raw API keys;
- `.env` files or deployment platform secrets.

Treat every dump as sensitive. A database dump and the application master key
together can expose stored secret values, so they must be stored and recovered
through separate approved channels.

## Prerequisites

Before scheduling production backups, operators should confirm:

- the target environment file points at the intended database;
- the Compose `postgres` service can be reached by the backup host;
- the backup destination has restricted access and storage encryption enabled;
- the application master key is recoverable through a separate secret manager or
  break-glass channel;
- a restore rehearsal has succeeded for the current schema generation.

The repository tooling sets local dump and checksum files to mode `600`, but it
does not provide off-host replication, retention automation or storage-level
encryption. Use the deployment platform or backup storage system for those
controls.

## Create A Backup

From the repository root, start or target the database service and run:

```bash
make up-db
make db-backup
```

By default, dumps are written under `dist/backups/postgres/` with a timestamped
file name. For an operator-managed location, set an explicit directory or file:

```bash
make db-backup BACKUP_DIR=/secure/operator/backups/postgres
make db-backup BACKUP_FILE=/secure/operator/backups/postgres/manual.dump
```

When the target environment uses a different Compose env file, pass it through
the existing `ENV_FILE` variable:

```bash
make db-backup ENV_FILE=.env.production BACKUP_DIR=/secure/operator/backups/postgres
```

Each successful backup writes:

- `<backup>.dump`
- `<backup>.dump.sha256`

Record the backup timestamp, source environment, dump location and checksum
verification result in the operational log. Do not record secret values, raw API
keys, environment files or the master key.

## Verify A Backup

Verify the checksum before moving or marking a backup as recoverable:

```bash
sha256sum -c /secure/operator/backups/postgres/manual.dump.sha256
```

Checksum verification proves file integrity only. It does not prove that the
dump can be restored or that the correct master key is available. Schedule
restore rehearsals in an isolated environment and keep the latest rehearsal
result with the backup inventory.

## Restore Readiness

Use `backend/docs/DISASTER_RECOVERY.md` before any destructive restore. At a
minimum, confirm:

- an incident owner approved replacing the target database state;
- application writers are stopped or traffic is drained;
- the selected dump and checksum match the intended recovery point;
- the master key and runtime configuration for that recovery point are available
  from the separate recovery channel;
- the target environment is isolated or is the intended production restore
  target.

The guarded restore command requires explicit confirmation:

```bash
sha256sum -c /secure/operator/backups/postgres/manual.dump.sha256
make db-restore BACKUP_FILE=/secure/operator/backups/postgres/manual.dump RESTORE_CONFIRM=replace
make db-current
```

After restore, run health, authentication, representative metadata reads, secret
decryption and audit checks before returning traffic.

## Rotation And Incidents

Take or identify a current backup before high-risk credential changes, bulk
secret rotations or master-key incident work. Use
`backend/docs/ROTATION_STRATEGY.md` for planned and incident-driven rotation of:

- stored secret values;
- MCP Secret Manager API keys;
- runtime signing secrets;
- PostgreSQL credentials;
- backup storage access;
- the application master key.

If a PostgreSQL dump and the application master key may both be exposed, assume
stored secret values are compromised and follow the incident rotation path.

## Related Documentation

- `db/README.md` documents database development commands and the local backup
  and restore targets.
- `backend/docs/DISASTER_RECOVERY.md` is the restore and disaster recovery
  runbook.
- `backend/docs/ROTATION_STRATEGY.md` covers routine and incident-driven
  credential rotation.
- `backend/docs/DEPLOYMENT.md` covers production runtime configuration and
  deployment readiness checks.
