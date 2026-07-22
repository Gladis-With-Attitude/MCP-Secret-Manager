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

## Reset

The reset workflow is destructive and reserved for local development:

```bash
make db-reset CONFIRM_RESET=dev
```

This drops the `public` schema, recreates it, and replays all migrations to
`head`. The command also requires `MCP_SECRET_MANAGER_ALLOW_DB_RESET=true`
inside the migration container, which the Makefile sets only for this target.
