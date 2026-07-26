# Deployment Guide

This guide covers runtime configuration only. It does not introduce production
infrastructure, new routes or authentication flows.

## Environments

The backend supports:

- `development`
- `test`
- `staging`
- `production`

Set the environment with:

```bash
MCP_SECRET_MANAGER_ENVIRONMENT=production
```

## Production Minimum

A production runtime must provide at least:

```bash
MCP_SECRET_MANAGER_ENVIRONMENT=production
MCP_SECRET_MANAGER_DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/mcp_secret_manager
MCP_SECRET_MANAGER_MASTER_KEY_BASE64=<base64-encoded-32-byte-key>
MCP_SECRET_MANAGER_MASTER_KEY_VERSION=1
MCP_SECRET_MANAGER_SECRET_KEY=<at-least-32-characters>
MCP_SECRET_MANAGER_TLS_REQUIRED=true
MCP_SECRET_MANAGER_SECURE_COOKIES=true
MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED=true
MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS=false
MCP_SECRET_MANAGER_OPENAPI_ENABLED=false
MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS=https://app.example.com
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL=admin@example.com
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME=Administrator
```

Do not commit production secrets. Inject them through the deployment platform's
secret manager.

## Startup Validation

The backend validates configuration before initializing repositories and use
cases. Invalid configuration stops startup with explicit messages that name the
missing or unsafe variable.

Safe configuration logs include only non-sensitive metadata such as environment,
port, enabled flags and whether sensitive values are configured.

The REST API emits baseline security headers by default: CSP constraints for
framing, base URIs and form posts, `X-Frame-Options: DENY`,
`X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` and a minimal
permissions policy. Production validation keeps those headers enabled, and
`Strict-Transport-Security` is added when
`MCP_SECRET_MANAGER_TLS_REQUIRED=true`. Keep `MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS`
to the exact frontend origins; wildcard and non-HTTPS origins are rejected in
production.

## Observability

Set `MCP_SECRET_MANAGER_LOG_JSON=true` in containerized or production-like
deployments when logs are collected by a structured log pipeline. Logs include
request ids and safe HTTP metadata, but never request bodies, authorization
headers, raw API keys or secret values.
Keep generic server access logs disabled unless the ingress layer can redact
paths and query strings, because the backend already emits sanitized route
template request logs.

The REST API exposes `GET /v1/metrics` with lightweight Prometheus-compatible
process-local HTTP request counters and duration totals.

Optional OpenTelemetry REST tracing is disabled by default. Enable it only when
an operator-controlled collector is available:

```bash
MCP_SECRET_MANAGER_OTEL_TRACES_ENABLED=true
MCP_SECRET_MANAGER_OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
```

The backend also honors OpenTelemetry trace propagation headers
(`traceparent`/`tracestate`) so upstream traces can correlate with backend
spans. Span attributes are intentionally limited to HTTP method, route template,
response status and request id. Do not configure header capture in the runtime
environment, and do not embed collector credentials in the OTLP endpoint URL.
Request bodies, authorization headers, API keys, session tokens, secret values,
secret names and secret descriptions must stay out of traces and logs.

The local Compose stack includes opt-in Prometheus and Grafana services for
operators who want to scrape and inspect the endpoint without adding managed
infrastructure:

```bash
make up-observability
curl -fsS http://127.0.0.1:8000/v1/metrics
curl -fsS 'http://127.0.0.1:9090/api/v1/targets?state=active'
```

Prometheus reads `monitoring/prometheus/prometheus.yml`, which scrapes
`backend:8000/v1/metrics` inside the Compose network. The Prometheus UI is bound
to `127.0.0.1:${PROMETHEUS_PORT:-9090}` by default and should stay restricted to
trusted operator networks. Set `PROMETHEUS_IMAGE` to a pinned image tag for
repeatable production-like deployments. If `/v1/metrics` is exposed outside a
private service network, protect it at the ingress or reverse proxy layer; the
metrics endpoint does not include request bodies, authorization headers, API
keys or secret values, but it can reveal operational metadata such as route
templates and status counts.

Grafana reads provisioning files from `monitoring/grafana/provisioning` and
loads the checked-in `monitoring/grafana/dashboards/secret-manager-overview.json`
dashboard. The dashboard uses only aggregate Prometheus metrics for REST request
counts, status codes and average duration; it does not include request bodies,
headers, API keys, secret values or example credentials. The local Grafana UI is
bound to `127.0.0.1:${GRAFANA_PORT:-3001}` by default and is configured for
anonymous viewer access so local operators can inspect the provisioned dashboard
without committing an admin password. Keep it behind trusted networks or add
deployment-specific authentication before exposing it elsewhere. Set
`GRAFANA_IMAGE` to a pinned image tag for repeatable production-like
deployments.

Validate the checked-in wiring before deployment changes with:

```bash
docker compose --env-file .env.example --profile observability config
```

## Backup And Recovery

The initial D5 backup foundation covers local and production-like PostgreSQL
operations through the root Makefile:

```bash
make db-backup
make db-restore BACKUP_FILE=dist/backups/postgres/manual.dump RESTORE_CONFIRM=replace
```

Backups are custom-format PostgreSQL dumps created by `pg_dump` with owner and
privilege statements removed, saved with local mode `600`, and accompanied by a
`sha256` checksum. Treat every dump as sensitive because it contains encrypted
secret values and metadata. Keep the application master key in a separate secret
manager or recovery channel; do not store it next to PostgreSQL backups.

Before a restore, stop application writers, verify the checksum, confirm that
the target database is the intended environment, then use
`RESTORE_CONFIRM=replace`. After restore, run migrations/current-state checks
and application smoke tests before returning traffic.
