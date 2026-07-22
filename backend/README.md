# MCP Secret Manager Backend

Backend FastAPI for MCP Secret Manager.

## Structure

- `backend/src/`: Clean Architecture backend source code.
- `backend/tests/`: backend unit, integration, security and e2e tests.
- `backend/docs/`: backend architecture, security, API, MCP and contribution documentation.
- `backend/configs/`: backend configuration examples without production secrets.
- `backend/Dockerfile`: backend development image used by the root Compose stack.

## Development

The recommended local workflow is the root Docker Compose stack:

```bash
make up
```

Backend-only Python commands can still be run from this directory when a local
Python environment is available.

## Docker

From the repository root:

```bash
make up
docker compose --env-file .env.example exec -T backend python -m pytest
```

The backend Docker image runs `infrastructure.bootstrap:app`, not the partial
presentation-only application. The bootstrap validates configuration, connects to
PostgreSQL, initializes repositories and use cases, injects the REST
dependencies, and disposes the database engine during FastAPI shutdown.

Database migrations are executed by the dedicated Compose `migrations` service
before the backend starts. The backend process itself does not run migrations.

System data bootstrap is executed by the dedicated Compose `bootstrap` service
after migrations and before the backend starts. It initializes permissions,
default roles and the configured administrator through
`backend/src/infrastructure/seed/`.

The bootstrap is idempotent and safe to replay:

```bash
make seed-run
```

Configuration lives in `.env`:

- `MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED`
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL`
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME`
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD`
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY`
- `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_ENABLED`
- `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_PROJECT_ID`
- `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_NAME`
- `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_API_KEY`

The current backend runtime supports API-key authentication. If
`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` is set, only its hash and prefix are
stored; the raw key is never logged. Password bootstrap is reserved until
password authentication is implemented.
