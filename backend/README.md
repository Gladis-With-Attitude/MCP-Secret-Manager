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

Migrations are not executed automatically during container startup.
