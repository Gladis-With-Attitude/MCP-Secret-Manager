# MCP Secret Manager

MCP Secret Manager is an open source, self-hosted secret manager for AI-first and
MCP-native infrastructure.

The repository is now organized as a monorepo:

- `backend/`: FastAPI backend, domain/application/infrastructure code, backend tests and backend docs.
- `frontend/`: Next.js 15 frontend bootstrap, providers, styles and frontend docs.
- `db/`: PostgreSQL migration assets.
- `docs/`: repository-level roadmap and cross-cutting project documentation.
- `docker-compose.yml`: local orchestration for backend, frontend and database.

## Installation

Use Docker for local development. The host does not need Node.js/npm, Python or
PostgreSQL dependencies installed to start the full stack.

```bash
cp .env.example .env
make up
```

See `docs/INSTALLATION_GUIDE.md` for prerequisites, first sign-in, local smoke
checks and the production configuration boundary.

## Scripts

```bash
make up       # build and start postgres, backend and frontend
make up-db    # start postgres only
make down     # stop the stack
make logs     # follow all service logs
make logs-db  # follow postgres logs only
make logs-bootstrap
make up-observability  # start opt-in Prometheus and Grafana
make docker-build
make docker-build-production
make db-current
make db-history
make db-upgrade
make db-downgrade DB_DOWN_REVISION=-1
make db-revision DB_REVISION_MESSAGE="describe change"
make db-reset CONFIRM_RESET=dev
make seed-run
make secret-scan
make dependency-scan
make release-artifacts RELEASE_VERSION=v0.1.0-rc.1
```

Backend and frontend validation scripts remain available through their own
directories when the corresponding toolchains are installed locally.

`make secret-scan` runs Gitleaks against repository history. `make dependency-scan`
audits backend dependencies with `pip-audit` through uv and frontend
dependencies with `npm audit`.

`make release-artifacts RELEASE_VERSION=...` creates an ignored
`dist/release/` source bundle, manifest, release notes stub and SHA-256 checksums.
The GitHub Actions release workflow uses the same target after the existing CI
quality, security, Docker and Playwright gates pass. Manual runs upload the
bundle as a workflow artifact; tag pushes matching `v*` also prepare a draft
GitHub Release without publishing container images or requiring extra secrets.

Docker-based validation can be run with:

```bash
make docker-build
make docker-build-production
docker compose --env-file .env.example exec -T backend python -m pytest
docker compose --env-file .env.example exec -T frontend npm run lint
docker compose --env-file .env.example exec -T frontend npm run typecheck
docker compose --env-file .env.example exec -T frontend npm run build
```

`make docker-build` keeps validating the development images used by the local
Compose stack. `make docker-build-production` validates the hardened production
targets, which use multi-stage builds, non-root runtime users and container
health checks.

The backend container starts the fully bootstrapped FastAPI application from
`infrastructure.bootstrap:app`. Runtime dependencies are wired to PostgreSQL
repositories through dependency overrides.

The Compose stack runs a one-shot `migrations` service before the backend. It
waits for PostgreSQL, executes `alembic upgrade head` with a PostgreSQL advisory
lock, and fails the stack startup if migrations fail. No manual migration step is
needed for local development.

After migrations, Compose runs a one-shot `bootstrap` service before the backend.
It initializes system permissions, default roles and the initial administrator
idempotently. Re-running it does not duplicate system data.

Initial administrator data is configured through `.env`:

```bash
MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED=true
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL=admin@example.local
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME=Administrator
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY=
```

`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` is optional and must be supplied by
the operator when API-key access is required. The value is hashed before storage
and is never logged. Password authentication is not implemented in the current
runtime, so `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` is reserved for future
auth wiring and is not persisted.

Seeds can be replayed manually with:

```bash
make seed-run
```

Runtime configuration is centralized under
`backend/src/infrastructure/configuration/` and documented in
`backend/docs/ENVIRONMENT.md`. The backend supports `development`, `test`,
`staging` and `production`, validates critical settings at startup, and logs only
non-sensitive configuration metadata.

## Architecture

The frontend uses Next.js 15, React 19, TypeScript, App Router, Tailwind CSS v4,
shadcn/ui, TanStack Query, React Hook Form, Zod and Lucide.

The backend remains a Clean Architecture FastAPI service. PostgreSQL runs as the
local persistence service and migrations live in `db/migrations`.

System data bootstrap lives in `backend/src/infrastructure/seed/`. It is an
infrastructure concern and is intentionally kept separate from REST routes and
business use cases.

Backend documentation lives in `backend/docs/`. Frontend documentation lives in
`frontend/docs/`. The project delivery roadmap lives in
`docs/PROJECT_ROADMAP.md`. The top-level user guide lives in
`docs/USER_GUIDE.md`, the administrator guide lives in
`docs/ADMINISTRATOR_GUIDE.md`, the installation guide lives in
`docs/INSTALLATION_GUIDE.md`, and the top-level operator backup entry point
lives in `docs/BACKUP_GUIDE.md`.

## Conventions

- Keep backend code inside `backend/`.
- Keep frontend code inside `frontend/`.
- Keep database migrations inside `db/`.
- Keep root files limited to orchestration and repository-level documentation.
- Do not store real secrets in `.env.example`, assets, docs or tests.
- Use Docker Compose as the default local workflow.

## Start

```bash
make up
```

Frontend: `http://127.0.0.1:3000`

Backend health: `http://127.0.0.1:8000/v1/health`

Prometheus UI, when the observability profile is enabled:
`http://127.0.0.1:9090`

Grafana UI, when the observability profile is enabled:
`http://127.0.0.1:3001`
