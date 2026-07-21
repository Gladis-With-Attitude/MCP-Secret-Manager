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
```

Migration commands should be run from the repository root or from a container
with access to both `backend/` and `db/` paths.
