# Disaster Recovery

This runbook covers operational recovery for the MCP Secret Manager
PostgreSQL database. It is written for the current D5 backup tooling: the root
Makefile targets call `scripts/postgres-backup.sh` and
`scripts/postgres-restore.sh` against the configured Compose `postgres`
service.

## Scope

The supported recovery artifact is a PostgreSQL custom-format dump plus its
`sha256` checksum. The dump contains encrypted secret values and metadata. It
does not contain the application master key, API keys in raw form or local
environment files.

Disaster recovery requires two independent recovery channels:

- PostgreSQL backup dump and checksum.
- Application master key and runtime configuration from the production secret
  manager or other approved recovery channel.

Never store the master key beside PostgreSQL dumps. A database dump plus the
master key can expose all stored secrets.

## Readiness Checklist

Before an incident, operators should keep the following ready:

- A documented backup location with restricted access.
- A separate, tested recovery path for the application master key.
- A restore host or environment where Compose can run the `postgres`,
  `migrations`, `bootstrap` and `backend` services.
- Recent recovery test notes with the backup timestamp used, restore duration
  and validation result.
- A clear decision owner for destructive restores.

The current repository tooling protects local backup files with mode `600` and
generates checksums. Encryption at rest and retention automation are future
production hardening items; until then, use the storage system's access control
and encryption features.

## Backup Procedure

Run backups from the repository root after selecting the environment file and
destination for the target environment:

```bash
make up-db
make db-backup
```

By default the dump is written to `dist/backups/postgres/`. For an operator
managed location, override the destination:

```bash
make db-backup BACKUP_DIR=/secure/operator/backups/postgres
make db-backup BACKUP_FILE=/secure/operator/backups/postgres/manual.dump
```

Each successful run writes:

- A custom-format PostgreSQL dump created with `pg_dump --format=custom`.
- A sibling checksum file named `<dump>.sha256`.

After backup, record the dump path, timestamp, source environment and checksum
verification status in the operational log. Do not paste secret values,
environment files or the master key into that log.

## Backup Verification

Verify every backup before treating it as recoverable:

```bash
sha256sum -c /secure/operator/backups/postgres/manual.dump.sha256
```

The checksum only proves file integrity. It does not prove that the dump can be
restored, that the master key is available or that the application can serve
traffic afterward. Schedule restore rehearsals in an isolated environment and
run the post-restore checks below.

## Restore Decision Gate

Restores are destructive for database objects in the target database because
`scripts/postgres-restore.sh` invokes `pg_restore --clean --if-exists` inside a
single transaction. Before running it, confirm:

- The incident owner approved replacing the target database state.
- Application writers are stopped or traffic is drained.
- The target Compose environment points at the intended PostgreSQL service.
- The selected dump and checksum match the intended recovery point.
- The application master key and runtime configuration for that recovery point
  are available through the separate recovery channel.

Do not restore into production while the application is still writing to the
same database.

## Restore Procedure

From the repository root, verify the checksum, restore the selected dump and
then check the migration state:

```bash
sha256sum -c /secure/operator/backups/postgres/manual.dump.sha256
make db-restore BACKUP_FILE=/secure/operator/backups/postgres/manual.dump RESTORE_CONFIRM=replace
make db-current
```

`RESTORE_CONFIRM=replace` is required intentionally. Without it, the restore
script exits before contacting Compose.

After the database restore, start or replay the normal infrastructure services
for the environment:

```bash
make seed-run
```

If the service was fully stopped, start it through the normal deployment path
after configuration and master-key recovery are complete.

## Post-Restore Validation

Before returning traffic, validate the restored environment:

- `make db-current` reports the expected migration head.
- `GET /v1/health` returns healthy from the backend.
- An administrator or service account can authenticate with a recovered,
  approved credential.
- Representative vault, project, secret metadata and secret-version history can
  be read.
- Secret value decryption succeeds with the recovered master key.
- Audit logs show only expected bootstrap or restore-time activity.

If any validation fails, keep traffic drained and preserve the failed restore
environment for investigation.

## Compromise Scenarios

If only a PostgreSQL dump is exposed, treat encrypted secret values and metadata
as sensitive but keep the master key isolated. Rotate storage credentials and
access paths that protected the dump.

If a dump and the application master key may both be exposed, assume stored
secret values are compromised. Restore availability first if needed, then rotate
application credentials, API keys and downstream secrets according to the
incident response plan.

If the master key is lost and no approved recovery copy exists, encrypted
secret values in PostgreSQL cannot be decrypted by the application. Preserve the
database for audit and rebuild affected secrets from their owners.

## Rehearsal Schedule

Run a recovery rehearsal after backup tooling changes, database migration
changes and before production readiness reviews. A rehearsal should restore the
latest backup into an isolated environment, run the post-restore validation
checks and record the observed restore duration and issues found.
