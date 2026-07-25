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

Runtime configuration is centralized in
`backend/src/infrastructure/configuration/` and exposed through the compatibility
facade `infrastructure.config`. Environment variables are documented in
`backend/docs/ENVIRONMENT.md`; production deployment requirements are documented
in `backend/docs/DEPLOYMENT.md`.

## Observability

REST responses include an `X-Request-ID` header. Clients can pass a valid
`X-Request-ID` value to correlate their own logs with backend logs; otherwise
the backend generates one per request.

The backend records one safe HTTP request log per REST request with method,
route template, status, duration and request id. Request bodies, authorization
headers, API keys and secret values are not logged. Set
`MCP_SECRET_MANAGER_LOG_JSON=true` to render structured JSON logs.

`GET /v1/metrics` exposes lightweight Prometheus-compatible request counters and
duration totals for the running process. It is intentionally minimal and does
not replace a full Prometheus/Grafana deployment.

Optional OpenTelemetry tracing can be enabled with
`MCP_SECRET_MANAGER_OTEL_TRACES_ENABLED=true`. Set
`MCP_SECRET_MANAGER_OTEL_EXPORTER_OTLP_ENDPOINT` when traces should be sent to a
specific OTLP/HTTP collector. REST spans include only the HTTP method, route
template, response status and request id; request bodies, authorization headers,
API keys, session tokens, secret values, names and descriptions are not added to
spans or logs.
