# Deployment Guide

This guide is the operator-facing deployment entry point for MCP Secret Manager.
It consolidates production deployment guidance across the repository and links
to the deeper backend, database, backup and administration references.

It does not introduce a managed hosting platform, Kubernetes manifests,
published container registry images or a hardened production Compose file. The
repository currently provides Docker development orchestration, production
Docker image targets, production configuration validation, database migration
tooling, bootstrap tooling and backup/restore scripts. Operators must supply
the surrounding production infrastructure.

## Scope

A production deployment is expected to run these application components:

- PostgreSQL 16 or a compatible managed PostgreSQL service;
- Alembic migrations from `db/migrations`;
- the idempotent bootstrap process for system permissions, default roles and
  the initial administrator;
- the FastAPI backend from `backend/Dockerfile` target `production`;
- the Next.js frontend from `frontend/Dockerfile` target `production`;
- optional Prometheus, Grafana and OpenTelemetry collector infrastructure.

The root `docker-compose.yml` remains the supported local orchestration path. It
is useful for understanding service order and validating production-like
configuration, but it uses development image targets, bind mounts and loopback
ports by default.

## Prerequisites

Before storing real secrets, operators should have:

- a deployment host or platform that can run the backend and frontend
  containers as non-root users;
- a PostgreSQL database reachable by the migration, bootstrap and backend
  runtimes;
- a reverse proxy or ingress that terminates HTTPS and forwards requests to the
  frontend and backend;
- a secret manager for runtime secrets, PostgreSQL credentials and first
  administrator API keys;
- a separate recovery channel for `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`;
- backup storage with restricted access and encryption at rest;
- an operational log for deployment, backup, restore and rollback decisions.

Do not commit production `.env` files, database passwords, API keys, signing
secrets, master keys or raw deployment logs containing secret material.

## Configuration Boundary

Use `.env.example` only as a local development template. Production values must
come from the deployment platform's secret/configuration mechanism or an
operator-controlled environment file that is not committed.

At minimum, production must provide:

```bash
MCP_SECRET_MANAGER_ENVIRONMENT=production
MCP_SECRET_MANAGER_DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/mcp_secret_manager
MCP_SECRET_MANAGER_MASTER_KEY_BASE64=<base64-encoded-32-byte-key>
MCP_SECRET_MANAGER_MASTER_KEY_VERSION=1
MCP_SECRET_MANAGER_SECRET_KEY=<at-least-32-characters>
MCP_SECRET_MANAGER_TLS_REQUIRED=true
MCP_SECRET_MANAGER_SECURE_COOKIES=true
MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED=true
MCP_SECRET_MANAGER_RATE_LIMIT_ENABLED=true
MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS=false
MCP_SECRET_MANAGER_OPENAPI_ENABLED=false
MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS=https://app.example.com
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL=admin@example.com
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME=Administrator
NEXT_PUBLIC_APP_ENV=production
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
```

`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` is optional. When it is used for
first access, provide an operator-generated key in this format:

```text
mcp_sm_<16 hex characters>_<64 hex characters>
```

The raw key is hashed before storage and is never logged. Keep the raw value in
the approved secret store because the application cannot display it after
bootstrap.

Password authentication is not implemented in the current runtime.
`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` is reserved for future auth wiring
and is not persisted today.

Validate production configuration before build or rollout:

```bash
make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production
```

The readiness command validates backend production security settings and public
frontend build settings without printing secret values. It rejects unsafe
production settings such as missing PostgreSQL configuration, placeholder master
keys, short signing secrets, debug mode, disabled TLS requirements, insecure
cookies, disabled security headers, disabled rate limiting, enabled OpenAPI,
development defaults, wildcard CORS origins and non-HTTPS production origins.

See `backend/docs/ENVIRONMENT.md` for the full variable reference.

## Build Artifacts

Validate the checked-in production Docker targets from the repository root:

```bash
make docker-build-production
```

The backend production image installs only runtime dependencies into a virtual
environment, runs as uid/gid `10001`, exposes port `8000` and checks
`/v1/health`.

The frontend production image builds the Next.js standalone server, runs as
uid/gid `10001`, exposes port `3000` and checks `/`.

The release workflow creates source release artifacts with:

```bash
make release-artifacts RELEASE_VERSION=v0.1.0-rc.1
```

Current repository automation does not publish container images. If an operator
pushes images to a registry, keep the image build inputs, tag, digest and source
commit recorded in the deployment log.

## Deployment Flow

Use this sequence for a staging or production rollout:

1. Build or select backend and frontend images from a reviewed source commit.
2. Prepare production runtime configuration and secrets outside the repository.
3. Run `make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production` against
   the intended environment file or equivalent generated file.
4. Confirm a recent PostgreSQL backup and separate master-key recovery path.
5. Apply database migrations before starting a new backend version.
6. Run the idempotent bootstrap process after migrations.
7. Start or replace backend containers and wait for `/v1/health`.
8. Start or replace frontend containers and wait for `/`.
9. Confirm ingress, TLS, CORS and cookie behavior from the public frontend
   origin.
10. Run readiness checks and record the deployed image tags, source commit,
    migration revision and validation result.

The local Compose stack expresses the same dependency order:

```text
postgres -> migrations -> bootstrap -> backend -> frontend
```

For local and production-like Compose validation, the normal stack starts
migrations and bootstrap before the backend:

```bash
make up
```

For production infrastructure, keep the same order in the deployment platform.
Do not rely on the backend process itself to run migrations; migrations are a
separate operational step.

## TLS And Reverse Proxy

The application expects HTTPS in production. The repository does not provide a
production reverse proxy configuration, certificate automation or public DNS
setup.

The reverse proxy or ingress should:

- terminate TLS for the public frontend and backend origins;
- forward frontend traffic to the Next.js server on port `3000`;
- forward API traffic to the FastAPI backend on port `8000`;
- preserve or generate request correlation headers where supported;
- protect `/v1/metrics` if it is exposed outside a private service network;
- avoid logging authorization headers, API keys, session cookies, request
  bodies or secret values.

Set `MCP_SECRET_MANAGER_TLS_REQUIRED=true` and
`MCP_SECRET_MANAGER_SECURE_COOKIES=true` in production. The backend emits HSTS
when TLS is required and validates that CORS origins use HTTPS.

`NEXT_PUBLIC_API_BASE_URL` must point at the public HTTPS backend origin used by
the browser.

## Migrations

Database migrations live under `db/migrations` and are executed by
`backend/scripts/manage-db.sh` through Makefile targets.

For the local Compose stack:

```bash
make db-current
make db-upgrade
make db-history
```

`docker compose up` runs migrations automatically through the one-shot
`migrations` service before the backend starts. The service waits for
PostgreSQL, runs `alembic upgrade head` and uses a PostgreSQL advisory lock so
concurrent migration commands cannot apply schema changes simultaneously.

In production, run migrations as an explicit deployment step with the same
application version and database configuration that the backend will use. Keep
application writers drained during high-risk migrations, and record the
migration revision before and after the rollout.

## Bootstrap And Admin Access

Bootstrap initializes:

- system permissions;
- default roles;
- the configured administrator identity;
- the administrator's global role assignment;
- optional initial API keys;
- optional service-account data when the referenced project already exists.

It does not create vaults, projects or secrets.

Bootstrap is idempotent and safe to replay:

```bash
make seed-run
```

After deployment, sign in with the bootstrapped administrator API key if one was
provided. Then use the administrator guide to assign scoped roles, create
service-account keys, verify audit visibility and revoke temporary access.

## Observability

Set structured logging for containerized production-like deployments:

```bash
MCP_SECRET_MANAGER_LOG_JSON=true
```

Backend request logs include safe metadata such as request id, method, route
template, status and duration. They must not include request bodies,
authorization headers, raw API keys, session tokens, master keys or secret
values.

The backend exposes:

```text
GET /v1/health
GET /v1/metrics
```

`/v1/metrics` returns lightweight Prometheus-compatible process-local HTTP
request counters and duration totals. The local Compose stack includes opt-in
Prometheus and Grafana wiring:

```bash
make up-observability
docker compose --env-file .env.example --profile observability config
```

Prometheus reads `monitoring/prometheus/prometheus.yml`. Grafana reads
provisioning from `monitoring/grafana/provisioning` and the checked-in dashboard
from `monitoring/grafana/dashboards/secret-manager-overview.json`.

Optional OpenTelemetry REST tracing is disabled by default. Enable it only when
an operator-controlled collector is available:

```bash
MCP_SECRET_MANAGER_OTEL_TRACES_ENABLED=true
MCP_SECRET_MANAGER_OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
```

Do not embed collector credentials in the OTLP endpoint URL or configure header
capture. Span attributes are intentionally limited to HTTP method, route
template, response status and request id.

## Backup And Restore Dependencies

Production deployments must have backup and restore procedures ready before
storing real secrets.

The current backup tooling creates PostgreSQL custom-format dumps through the
Compose `postgres` service:

```bash
make db-backup
make db-restore BACKUP_FILE=/secure/operator/backups/postgres/manual.dump RESTORE_CONFIRM=replace
```

Each backup writes a dump and sibling `sha256` checksum. Treat dumps as
sensitive because they contain encrypted secret values, hashed API key material
and metadata. The application master key is not stored in PostgreSQL; keep it in
a separate secret manager or recovery channel.

Before restore, drain application writers, verify the checksum and confirm that
the selected dump, target database and recovered master key belong together.
After restore, run migrations/current-state checks and application smoke tests
before returning traffic.

Use `docs/BACKUP_GUIDE.md` and `backend/docs/DISASTER_RECOVERY.md` for the full
operator flow.

## Readiness Checks

Run these checks before sending user or MCP traffic to a new deployment:

```bash
make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production
make docker-build-production
make db-current
```

Then verify from the deployed environment:

- backend health returns `{"status":"ok"}` from `/v1/health`;
- frontend health check path `/` returns a non-5xx response;
- the public frontend origin can call the public backend origin;
- HTTPS, secure cookies, CORS and CSRF behavior match the configured origins;
- an administrator or service account can authenticate with an approved API key;
- representative vault, project and secret metadata can be read;
- a controlled secret reveal works only for an actor with `secret.decrypt`;
- audit logs record authentication and sensitive operations;
- metrics scraping works from the trusted observability network;
- no logs include raw API keys, authorization headers, session tokens, master
  keys or secret values.

## Rollback And Upgrade Handoffs

The repository does not yet include a dedicated upgrade guide. Until D6f is
complete, record rollback and upgrade handoffs in the deployment runbook for the
target environment.

Before rollout:

- record the current source commit, image tags or digests and migration
  revision;
- confirm the latest backup and checksum;
- confirm the matching master key and runtime configuration recovery path;
- identify whether the deployment includes database migrations.

If rollback is needed:

- restore the previous backend and frontend images when no incompatible
  migration has been applied;
- keep traffic drained if the migration changed schema compatibility;
- use `backend/docs/DISASTER_RECOVERY.md` before destructive database restore;
- replay bootstrap only after the target database and application version are
  known to match;
- run the readiness checks again before returning traffic.

Credential rotation, master-key incident decisions and post-compromise handling
belong in `backend/docs/ROTATION_STRATEGY.md`.

## Related Documentation

- `README.md` lists the repository layout and common commands.
- `docs/INSTALLATION_GUIDE.md` covers local Docker Compose installation.
- `docs/ADMINISTRATOR_GUIDE.md` covers administrator access, RBAC, API keys,
  observability and routine operator checks.
- `docs/BACKUP_GUIDE.md` is the top-level backup entry point.
- `backend/docs/DEPLOYMENT.md` covers backend runtime deployment details.
- `backend/docs/ENVIRONMENT.md` documents environment variables and production
  validation rules.
- `backend/docs/DISASTER_RECOVERY.md` is the restore and disaster recovery
  runbook.
- `backend/docs/ROTATION_STRATEGY.md` covers planned and incident-driven
  credential rotation.
- `db/README.md` documents database migration, backup and restore commands.
