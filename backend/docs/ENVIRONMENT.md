# Runtime Environment Variables

All backend runtime configuration is centralized in
`backend/src/infrastructure/configuration/`.

Supported environments:

- `development`
- `test`
- `staging`
- `production`

The backend validates runtime configuration at startup and fails fast with an
explicit `ConfigurationError` when a critical setting is missing or unsafe.

## Variables

| Variable | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| `MCP_SECRET_MANAGER_ENVIRONMENT` | enum | `development` | yes | Runtime environment: `development`, `test`, `staging`, `production`. |
| `MCP_SECRET_MANAGER_SERVICE_NAME` | string | `mcp-secret-manager` | no | Public service name used by health checks and logs. |
| `MCP_SECRET_MANAGER_DEBUG` | boolean | `false` | no | Enables debug behavior. Must be `false` in production. |
| `MCP_SECRET_MANAGER_LOG_LEVEL` | enum | `INFO` | no | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. |
| `MCP_SECRET_MANAGER_LOG_JSON` | boolean | `false` | no | Enables structured JSON logs with safe redaction. |
| `MCP_SECRET_MANAGER_OTEL_TRACES_ENABLED` | boolean | `false` | no | Enables optional OpenTelemetry server spans for REST requests. |
| `MCP_SECRET_MANAGER_OTEL_EXPORTER_OTLP_ENDPOINT` | string | none | no | Optional OTLP/HTTP traces endpoint. Leave empty to use OpenTelemetry exporter defaults. Do not embed credentials in the URL. |
| `MCP_SECRET_MANAGER_DATABASE_URL` | string | none | yes except `test` | SQLAlchemy URL for PostgreSQL. Must use `postgresql+asyncpg`. |
| `MCP_SECRET_MANAGER_ALEMBIC_CONFIG` | string | auto-detected | no | Alembic configuration path for migration commands. |
| `MCP_SECRET_MANAGER_MIGRATION_WAIT_TIMEOUT_SECONDS` | integer | `60` | no | PostgreSQL readiness timeout for migrations. |
| `MCP_SECRET_MANAGER_MIGRATION_LOCK_TIMEOUT_SECONDS` | integer | `300` | no | Advisory-lock wait timeout for migrations. |
| `MCP_SECRET_MANAGER_SECRET_KEY` | string | none | staging/production | Runtime signing secret. Must be at least 32 characters when set. |
| `MCP_SECRET_MANAGER_TLS_REQUIRED` | boolean | `false` | production | Must be `true` in production. |
| `MCP_SECRET_MANAGER_SECURE_COOKIES` | boolean | `false` | production | Must be `true` in production. |
| `MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS` | boolean | `true` | no | Allows development placeholders. Must be `false` in production. |
| `MCP_SECRET_MANAGER_MASTER_KEY_BASE64` | string | none | yes except `test` | Base64 encoded 32-byte cryptography master key. |
| `MCP_SECRET_MANAGER_MASTER_KEY_VERSION` | integer | `1` | no | Master key version, must be greater than or equal to `1`. |
| `MCP_SECRET_MANAGER_REST_HOST` | string | `127.0.0.1` | no | REST bind host. |
| `MCP_SECRET_MANAGER_REST_PORT` | integer | `8000` | no | REST bind port. |
| `MCP_SECRET_MANAGER_OPENAPI_ENABLED` | boolean | `true` | no | Enables OpenAPI docs. Must be `false` in production. |
| `MCP_SECRET_MANAGER_CORS_ALLOWED_ORIGINS` | CSV string | local frontend origins | yes | Allowed CORS origins. Production origins must use HTTPS. |
| `MCP_SECRET_MANAGER_CORS_ALLOWED_METHODS` | CSV string | common REST methods | yes | Allowed CORS methods. |
| `MCP_SECRET_MANAGER_CORS_ALLOWED_HEADERS` | CSV string | `Authorization,Content-Type,X-CSRF-Token` | yes | Allowed CORS headers. |
| `MCP_SECRET_MANAGER_CORS_ALLOW_CREDENTIALS` | boolean | `true` | no | Whether CORS credentials are allowed. Cannot be used with wildcard origins. Production rejects wildcard origins. |
| `MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED` | boolean | `true` | no | Enables baseline REST security headers. Must be `true` in production. HSTS is emitted when `MCP_SECRET_MANAGER_TLS_REQUIRED=true`. |
| `MCP_SECRET_MANAGER_RATE_LIMIT_ENABLED` | boolean | `true` | no | Enables in-process REST rate limiting. Must be `true` in production. |
| `MCP_SECRET_MANAGER_RATE_LIMIT_REQUESTS` | integer | `120` | no | Maximum counted REST requests per client and window. |
| `MCP_SECRET_MANAGER_RATE_LIMIT_WINDOW_SECONDS` | integer | `60` | no | Fixed-window duration for REST rate limiting. |
| `MCP_SECRET_MANAGER_RATE_LIMIT_EXEMPT_PATHS` | CSV string | `/v1/health,/v1/metrics` | no | Paths excluded from REST rate limiting for probes and scrapes. |
| `MCP_SECRET_MANAGER_RATE_LIMIT_MAX_CLIENTS` | integer | `10000` | no | Maximum in-memory client windows kept per process before oldest entries are pruned. |
| `MCP_SECRET_MANAGER_MCP_ENABLED` | boolean | `true` | no | Enables MCP runtime configuration. |
| `MCP_SECRET_MANAGER_DOCKER_ENABLED` | boolean | `false` | no | Marks the runtime as Docker-managed. |
| `MCP_SECRET_MANAGER_AUDIT_RETENTION_DAYS` | integer | `365` | no | Audit retention window in days. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED` | boolean | `true` | no | Enables system data bootstrap. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL` | string | none | if bootstrap enabled | Initial administrator email. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME` | string | none | if bootstrap enabled | Initial administrator display name. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` | string | none | no | Reserved for future password auth; not persisted today. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` | string | none | no | Optional initial admin API key. Raw value is never logged. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_ENABLED` | boolean | `false` | no | Enables optional service account seed. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_PROJECT_ID` | UUID string | none | if service account seed enabled | Existing project id for optional service account seed. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_NAME` | string | none | if service account seed enabled | Optional service account name. |
| `MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_API_KEY` | string | none | no | Optional service account API key. Raw value is never logged. |
| `MCP_SECRET_MANAGER_ALLOW_DB_RESET` | boolean | none | dev command only | Required by `make db-reset`; never set in production. |
| `MCP_SECRET_MANAGER_TEST_DATABASE_URL` | string | none | integration tests only | PostgreSQL URL used by optional DB integration tests. |

Frontend variables:

| Variable | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_APP_ENV` | string | `development` | no | Frontend runtime label. |
| `NEXT_PUBLIC_API_BASE_URL` | URL | `http://127.0.0.1:8000` | yes | REST API base URL used by the frontend. |
| `FRONTEND_PORT` | integer | `3000` | no | Local frontend port binding. |

PostgreSQL Compose variables:

| Variable | Type | Default | Required | Description |
| --- | --- | --- | --- | --- |
| `POSTGRES_DB` | string | `mcp_secret_manager` | no | Local PostgreSQL database name. |
| `POSTGRES_USER` | string | `mcp_secret_manager` | no | Local PostgreSQL user. |
| `POSTGRES_PASSWORD` | string | development placeholder | no | Local PostgreSQL password. Do not reuse in production. |
| `POSTGRES_PORT` | integer | `5432` | no | Local PostgreSQL port binding. |

## Production Rules

Production validation rejects:

- missing `MCP_SECRET_MANAGER_DATABASE_URL`;
- missing or invalid `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`;
- missing or short `MCP_SECRET_MANAGER_SECRET_KEY`;
- `MCP_SECRET_MANAGER_DEBUG=true`;
- `MCP_SECRET_MANAGER_OPENAPI_ENABLED=true`;
- `MCP_SECRET_MANAGER_TLS_REQUIRED=false`;
- `MCP_SECRET_MANAGER_SECURE_COOKIES=false`;
- `MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED=false`;
- `MCP_SECRET_MANAGER_RATE_LIMIT_ENABLED=false`;
- `MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS=true`;
- non-HTTPS CORS origins;
- wildcard CORS origins in production or when credentials are enabled.

Safe configuration logs expose only non-sensitive metadata. Passwords, API keys,
tokens, master keys and secret keys are never logged.

## Observability

REST responses include baseline security headers, including CSP, frame denial,
MIME sniffing protection, referrer policy and permissions policy. HSTS is added
when TLS is required. Responses also include `X-Request-ID`. A client-supplied
valid `X-Request-ID` is echoed back; otherwise the backend generates one.
Request logs include only safe metadata: request id, method, route template,
status code and duration.

`GET /v1/metrics` exposes lightweight Prometheus-compatible counters and
duration totals for HTTP requests in the current process. Metrics labels use
route templates where the REST router has resolved them; request bodies,
authorization headers, raw API keys and secret values are not exposed.

## REST Rate Limiting

REST rate limiting uses local in-process fixed windows keyed by the direct client
address seen by the ASGI server. It is intentionally simple and requires no
external storage, so limits are best-effort across multiple workers or after a
process restart. Responses include `RateLimit-Limit`, `RateLimit-Remaining` and
`RateLimit-Reset`; rejected requests return `429` with `Retry-After`.

`/v1/health` and `/v1/metrics` are exempt by default so readiness checks and
Prometheus scrapes do not consume client budgets.
