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

## Observability

Set `MCP_SECRET_MANAGER_LOG_JSON=true` in containerized or production-like
deployments when logs are collected by a structured log pipeline. Logs include
request ids and safe HTTP metadata, but never request bodies, authorization
headers, raw API keys or secret values.

The REST API exposes `GET /v1/metrics` with lightweight Prometheus-compatible
process-local HTTP request counters and duration totals. Full Prometheus
scraping, Grafana dashboards and OpenTelemetry tracing remain separate D1
follow-up work.
