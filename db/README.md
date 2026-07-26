# MCP Secret Manager Database

Database migrations and database-specific development assets live here.

PostgreSQL is started by the root Docker Compose stack.

## Structure

- `migrations/`: Alembic migration environment and versions.
- `alembic.ini`: Alembic configuration, with paths adjusted for the monorepo.
- `config/`: future non-secret database configuration templates.

## Development

From the repository root:

```bash
make up-db
make up
make db-current
make db-history
make db-upgrade
make db-downgrade DB_DOWN_REVISION=-1
make db-revision DB_REVISION_MESSAGE="describe change"
```

`docker compose up` runs migrations automatically through the one-shot
`migrations` service before the backend starts. The service waits for PostgreSQL,
runs `alembic upgrade head`, and uses a PostgreSQL advisory lock so concurrent
migration commands cannot apply schema changes simultaneously.

Manual migration commands should be run through the Makefile from the repository
root. They execute inside the backend image with both `backend/` and `db/`
mounted.

## Backup

The first local PostgreSQL backup workflow uses the existing Compose
`postgres` service and writes a custom-format `pg_dump` file plus a `sha256`
checksum:

```bash
make up-db
make db-backup
```

By default backups are written under `dist/backups/postgres/` with file mode
`600`. Override the location when needed:

```bash
make db-backup BACKUP_FILE=dist/backups/postgres/manual.dump
make db-backup BACKUP_DIR=/secure/operator/backups/postgres
```

The dump contains PostgreSQL data, encrypted secret values and metadata. It
must be handled as sensitive operational data even though the application master
key is not stored in PostgreSQL and must not be colocated with database dumps.

## Restore

Restore is intentionally explicit because it replaces database objects from the
selected dump. Stop application writers first, verify the checksum, then run:

```bash
sha256sum -c dist/backups/postgres/manual.dump.sha256
make db-restore BACKUP_FILE=dist/backups/postgres/manual.dump RESTORE_CONFIRM=replace
make db-current
```

After restore, validate the application with the normal smoke or test workflow
before returning traffic to the restored database.

For full incident handling, restore decision gates and post-restore validation,
use `backend/docs/DISASTER_RECOVERY.md`.

## Reset

The reset workflow is destructive and reserved for local development:

```bash
make db-reset CONFIRM_RESET=dev
```

This drops the `public` schema, recreates it, and replays all migrations to
`head`. The command also requires `MCP_SECRET_MANAGER_ALLOW_DB_RESET=true`
inside the migration container, which the Makefile sets only for this target.
