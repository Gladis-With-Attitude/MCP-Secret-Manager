# Installation Guide

This guide is the installation entry point for MCP Secret Manager. It covers the
supported local Docker Compose installation path and the first checks required
before users or MCP clients rely on the service.

It does not cover production deployment architecture, upgrades, backups or
day-to-day administration in detail. Use the related documentation links at the
end for those topics.

## Scope

The repository is designed to run as a local monorepo stack:

- PostgreSQL 16 for persistence;
- a one-shot migration service that applies Alembic migrations;
- a one-shot bootstrap service that seeds system permissions, roles and the
  initial administrator;
- a FastAPI backend;
- a Next.js frontend;
- optional Prometheus and Grafana services for local observability.

Docker Compose is the default installation path. The host does not need local
Python, Node.js or PostgreSQL packages to start the stack.

## Prerequisites

Install these host tools before starting:

- Docker with the Compose v2 plugin available as `docker compose`;
- `make`;
- `git`;
- a browser that can reach local loopback addresses.

Confirm Docker can run containers:

```bash
docker compose version
docker ps
```

If Docker requires elevated privileges on the host, configure Docker access
through the host operating system instead of running repository commands with
unnecessary privileges.

## Get The Source

Clone the repository and enter the working tree:

```bash
git clone https://github.com/TheoCo27/MCP-Secret-Manager.git
cd MCP-Secret-Manager
```

For contributor work on a fork, use the fork URL and the active feature branch
provided by the maintainer.

## Configure Local Development

Create a local environment file from the example:

```bash
cp .env.example .env
```

The example values are for local development only. They include placeholder
database credentials, a development signing secret, insecure local cookies and a
development master key. Do not reuse `.env.example` values for staging or
production.

For a local install, review at least these values:

- `POSTGRES_PORT`: change when another PostgreSQL service already uses `5432`.
- `FRONTEND_PORT`: change when another frontend already uses `3000`.
- `MCP_SECRET_MANAGER_REST_PORT`: change when another backend already uses
  `8000`.
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL`: set the initial administrator
  email for local testing.
- `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY`: optionally supply an
  operator-generated API key for initial sign-in.

When supplying an initial administrator API key, use the current accepted
format:

```text
mcp_sm_<16 hex characters>_<64 hex characters>
```

The raw key is hashed before storage and is never logged. Store the raw value in
a safe local secret store because the application cannot display it after
bootstrap.

Password authentication is not implemented in the current runtime.
`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` is reserved for future auth wiring
and is not persisted today.

## Start The Stack

Start the full local stack from the repository root:

```bash
make up
```

This command builds the development images and starts PostgreSQL, migrations,
bootstrap, backend and frontend. The backend waits for the database, migrations
and bootstrap before serving requests. No separate migration command is required
for the normal local installation path.

Open the application:

```text
http://127.0.0.1:3000
```

Check the backend health endpoint:

```text
http://127.0.0.1:8000/v1/health
```

If startup fails, inspect service logs:

```bash
make logs
make logs-bootstrap
```

Do not paste raw API keys, `.env` files, database passwords or master keys into
tickets, chats or log excerpts.

## Sign In For The First Time

If `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` was set before the first
bootstrap run, use that API key on the frontend sign-in screen.

If no initial API key was provided, the administrator identity and default roles
are still seeded, but there is no password sign-in flow in the current runtime.
Create or seed an API key through an approved operator workflow before expecting
browser, REST or MCP access.

After signing in, use the administrator guide to assign scoped roles, create
service-account keys and verify audit visibility.

## Common Local Operations

Stop the stack:

```bash
make down
```

Start only PostgreSQL:

```bash
make up-db
```

Replay idempotent bootstrap data:

```bash
make seed-run
```

Inspect the current migration revision:

```bash
make db-current
```

Start optional local observability:

```bash
make up-observability
```

Prometheus is available at `http://127.0.0.1:9090`. Grafana is available at
`http://127.0.0.1:3001`.

## Local Validation

For an installation smoke check, run:

```bash
make docker-build
make up
docker compose --env-file .env.example exec -T backend python -m pytest
docker compose --env-file .env.example exec -T frontend npm run lint
docker compose --env-file .env.example exec -T frontend npm run typecheck
docker compose --env-file .env.example exec -T frontend npm run build
```

Backend and frontend validation scripts can also be run directly from their own
directories when the corresponding local toolchains are installed.

## Production Boundary

The local installation path is not a production deployment recipe. Before
building a staging or production environment:

- generate a non-placeholder 32-byte `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`;
- generate a non-placeholder `MCP_SECRET_MANAGER_SECRET_KEY`;
- set `MCP_SECRET_MANAGER_ENVIRONMENT=production`;
- disable insecure development defaults;
- require TLS and secure cookies;
- disable OpenAPI in production;
- use HTTPS CORS origins;
- protect PostgreSQL credentials, API keys, signing secrets and the master key
  in the deployment secret manager.

Validate a production environment file before rollout:

```bash
make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production
```

Production backup, restore and rotation procedures must be prepared before
storing real secrets.

## Related Documentation

- `README.md` lists the top-level repository layout and common commands.
- `backend/docs/ENVIRONMENT.md` documents runtime configuration and production
  validation rules.
- `docs/ADMINISTRATOR_GUIDE.md` covers bootstrap, RBAC, API keys, audit review
  and routine operator checks.
- `docs/USER_GUIDE.md` explains browser and MCP workflows after installation.
- `docs/BACKUP_GUIDE.md` is the operator-facing backup entry point.
- `docs/DEPLOYMENT_GUIDE.md` is the operator-facing production deployment entry
  point.
- `backend/docs/DEPLOYMENT.md` covers production deployment readiness.
