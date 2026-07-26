# Administrator Guide

This guide is the administrator and operator entry point for MCP Secret Manager.
It covers the current production-readiness runtime: bootstrap, administrator
access, RBAC, API keys, audit review, observability, backup coordination and
routine operational checks.

It does not cover installation, deployment architecture or end-user workflows in
detail. Use the related documentation links at the end for those topics.

## Administrator Scope

Administrators are responsible for:

- keeping production configuration valid and non-secret in logs;
- protecting the application master key, runtime signing secret and database
  credentials;
- bootstrapping the initial administrator identity and any first API key;
- assigning roles through the RBAC model;
- creating and revoking API keys for humans, service accounts and MCP clients;
- reviewing audit events after sensitive changes;
- running backup, recovery and rotation procedures;
- keeping observability endpoints and dashboards on trusted networks.

Administrators must still follow least privilege. Use a broad administrator key
only for setup, recovery and explicit administration. Day-to-day automation
should use a narrower user or service-account identity with scoped role
assignments.

## Bootstrap

The local Compose runtime starts services in this order:

1. `postgres`
2. `migrations`
3. `bootstrap`
4. `backend`
5. `frontend`

The bootstrap creates system permissions, default roles, the configured
administrator user, the administrator's global role assignment and optional API
keys. It does not create vaults, projects or secrets.

Configure the initial administrator through the deployment environment:

```bash
MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED=true
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL=admin@example.local
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME=Administrator
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY=
```

`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` is optional. When API-key access is
needed for the initial administrator, supply an operator-generated key through
the deployment secret channel. The key must use the current format:

```text
mcp_sm_<16 hex characters>_<64 hex characters>
```

The raw key is hashed before storage and is never logged. Store the raw value in
the approved operator secret store because the application cannot display it
after bootstrap.

Password authentication is not implemented in the current runtime.
`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` is reserved configuration and is
not persisted today.

Re-run idempotent seeds when needed:

```bash
make seed-run
```

If bootstrap fails, inspect safe bootstrap logs:

```bash
make logs-bootstrap
```

Do not paste raw API keys, master keys, `.env` files or database passwords into
tickets, chats or log excerpts.

## Administrator Sign-In

The browser console signs in with an API key and exchanges it for an HTTP-only
session cookie. In local development the frontend normally runs at:

```text
http://127.0.0.1:3000
```

For direct REST administration, send the API key as a bearer token:

```bash
curl -fsS \
  -H "Authorization: Bearer $MCP_SM_ADMIN_API_KEY" \
  http://127.0.0.1:8000/v1/health
```

Browser sessions use the `mcp_sm_session` HTTP-only cookie. Unsafe requests made
with that cookie also require the double-submit CSRF token from the readable
`mcp_sm_csrf` cookie in the `X-CSRF-Token` header. Bearer API-key requests do
not use the session CSRF flow.

Revoke sessions from `Profile` when a browser, device or operator boundary is no
longer trusted.

## Roles And Permissions

Bootstrap seeds these default roles:

- `administrator`: all default permissions.
- `user`: day-to-day metadata, rotation, project archive and API-key management
  permissions, without secret value decrypt permission.
- `readonly`: read permissions for metadata, roles and audit events, without
  secret value decrypt permission.

Default permissions are:

```text
vault.create      vault.read      vault.update      vault.archive
project.create    project.read    project.update    project.archive
secret.create     secret.read     secret.update     secret.archive
secret.delete     secret.decrypt  secret.rotate
apikey.create     apikey.read     apikey.update     apikey.revoke
role.read         role.create     role.update       role.assign
role.revoke       audit.read
```

Secret metadata access and secret value access are separate. `secret.read`
allows metadata and version metadata reads. `secret.decrypt` is required to
return a stored secret value. `secret.rotate` is required to create or restore a
secret value version.

Role assignments can be scoped to:

- `global`: applies everywhere.
- `vault`: applies to that vault, projects inside it and secrets inside those
  projects.
- `project`: applies to that project and secrets inside it.
- `secret`: applies to one secret resource.

Use the smallest practical scope. Prefer project or vault assignments for MCP
clients and service accounts instead of global assignments. For secret value
readers, grant `secret.decrypt` only where value access is operationally
required.

The RBAC console exposes permissions, roles, role creation, role editing, actor
role assignment and role revocation. System roles are seeded by bootstrap; keep
custom roles narrow and named for the operational boundary they serve.

## API Keys And Service Accounts

API keys authenticate browser sessions, REST clients, MCP clients and service
accounts. The full generated key is shown only once when created by the
application. Existing key records expose metadata such as id, name, owner,
prefix, status, expiration and timestamps, but not the raw key.

Use this lifecycle for every key:

1. Create a dedicated identity or choose the correct existing owner.
2. Assign the owner the smallest role and scope needed.
3. Create an API key with a clear non-sensitive name and expiration when policy
   requires one.
4. Store the raw key in the approved secret store immediately.
5. Test only the required workflow.
6. Revoke the key when the user, service, MCP client or incident no longer
   justifies access.

API key permission and scope fields are stored with the key record for
operational inventory and client intent. Current REST authorization is evaluated
against the authenticated owner identity and its RBAC role assignments, so do
not rely on broad owner roles being narrowed only by API-key metadata.

For MCP clients and automation, prefer service-account ownership. Bootstrap can
seed an optional service account only when the referenced project already
exists:

```bash
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_ENABLED=true
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_PROJECT_ID=<existing-project-id>
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_NAME=openclaw-agent-prod
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_API_KEY=
```

Use regular administration workflows after the first project exists when that is
clearer than replaying bootstrap configuration.

## Vault, Project And Secret Administration

Use vaults as security boundaries and projects as application or agent
boundaries. Names, descriptions, tags, metadata, rotation notes and audit
context are visible metadata and must not contain secret values.

Recommended operating pattern:

1. Create a vault for an environment, tenant or trust boundary.
2. Assign operators or service accounts to that vault only when they need broad
   access inside it.
3. Create projects for individual applications, agents or MCP servers.
4. Assign project-scoped roles for routine automation.
5. Create secrets with safe metadata and an initial value.
6. Reveal values only through explicit `secret.decrypt` access.
7. Rotate values by creating a new current version.
8. Archive retired vaults, projects or secrets instead of reusing ambiguous
   names.

The current runtime intentionally avoids bulk secret value reads. Metadata list
operations do not return secret values.

## Audit Review

Audit events are security records. Review `Audit Logs` after:

- administrator sign-in and session changes;
- vault, project and secret lifecycle changes;
- explicit secret value reads;
- secret rotation or version restore;
- API-key creation, update or revocation;
- role creation, update, assignment or revocation;
- backup, restore or incident-driven credential work.

Useful filters include actor id, action, resource type, resource id, result,
time range and search text. Audit entries should include safe metadata such as
ids, counts, request id, actor and result. They must not include secret values,
raw API keys, authorization headers, session tokens, master keys or request
bodies.

Repeated `permission.denied`, authentication failures, unexpected value reads or
unknown actors should trigger key review, session revocation and, when needed,
the incident rotation path.

## Production Security Controls

Validate production environment files before rollout:

```bash
make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production
```

Production validation requires safe runtime settings, including:

- `MCP_SECRET_MANAGER_ENVIRONMENT=production`;
- a valid PostgreSQL URL using `postgresql+asyncpg`;
- a non-placeholder 32-byte `MCP_SECRET_MANAGER_MASTER_KEY_BASE64`;
- a runtime `MCP_SECRET_MANAGER_SECRET_KEY` of at least 32 characters;
- `MCP_SECRET_MANAGER_TLS_REQUIRED=true`;
- `MCP_SECRET_MANAGER_SECURE_COOKIES=true`;
- `MCP_SECRET_MANAGER_SECURITY_HEADERS_ENABLED=true`;
- `MCP_SECRET_MANAGER_RATE_LIMIT_ENABLED=true`;
- `MCP_SECRET_MANAGER_ALLOW_INSECURE_DEV_DEFAULTS=false`;
- `MCP_SECRET_MANAGER_OPENAPI_ENABLED=false`;
- exact HTTPS CORS origins, without wildcards.

Keep the application master key separate from PostgreSQL backups. A database
dump plus the matching master key can expose stored secret values.

## Observability

Every REST response includes `X-Request-ID`. Logs and traces use safe metadata:
method, route template, status, duration and request id. They must not include
request bodies, authorization headers, raw API keys, session tokens, secret
values, secret names or secret descriptions.

Enable structured logs in production-like deployments when collected by a log
pipeline:

```bash
MCP_SECRET_MANAGER_LOG_JSON=true
```

The backend exposes Prometheus-compatible process-local metrics at:

```text
GET /v1/metrics
```

The local observability profile starts Prometheus and Grafana:

```bash
make up-observability
```

Keep Prometheus and Grafana bound to trusted operator networks. The checked-in
Grafana dashboard shows aggregate REST request counts, status codes and average
duration only.

OpenTelemetry REST tracing is disabled by default. Enable it only with an
operator-controlled collector and do not configure header capture:

```bash
MCP_SECRET_MANAGER_OTEL_TRACES_ENABLED=true
MCP_SECRET_MANAGER_OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
```

## Backup, Restore And Rotation

Before high-risk changes, identify or create a current PostgreSQL backup:

```bash
make db-backup ENV_FILE=.env.production BACKUP_DIR=/secure/operator/backups/postgres
sha256sum -c /secure/operator/backups/postgres/<backup>.dump.sha256
```

Use `docs/BACKUP_GUIDE.md` for backup handling and
`backend/docs/DISASTER_RECOVERY.md` before any destructive restore. A restore
requires explicit confirmation:

```bash
make db-restore BACKUP_FILE=/secure/operator/backups/postgres/<backup>.dump RESTORE_CONFIRM=replace
make db-current
```

After restore, validate health, migrations, administrator sign-in,
representative metadata reads, explicit secret decryption and audit events
before returning traffic.

Use `backend/docs/ROTATION_STRATEGY.md` for planned and incident-driven
rotation of stored secret values, MCP Secret Manager API keys, runtime signing
secrets, PostgreSQL credentials, backup access and the application master key.

## Routine Operator Checklist

- Run `make deployment-readiness` before production configuration changes.
- Confirm `/v1/health` after deploys, restores and runtime restarts.
- Review audit logs after administrative or secret-value work.
- Keep administrator API keys rare, stored in the approved secret store and
  rotated after personnel or device changes.
- Use project- or vault-scoped service-account roles for MCP clients.
- Revoke unused sessions and API keys.
- Keep backups, checksums and master-key recovery material in separate channels.
- Rehearse restore in an isolated environment after schema or backup workflow
  changes.
- Keep metrics and dashboard access private.
- Run `make secret-scan` and `make dependency-scan` before release-sensitive
  changes when local tool access is available.

## Common Administrator Errors

`Invalid authentication credentials.`

The API key is malformed, unknown, expired, revoked or copied incorrectly. Check
the key prefix in API-key metadata when available, then revoke and replace the
key if exposure or uncertainty exists.

`Authentication is required.`

The request did not include a valid bearer API key or browser session. For REST
scripts, check the `Authorization: Bearer ...` header. For browser sessions,
sign in again.

`CSRF token is missing or invalid.`

The request is using the browser session cookie for an unsafe method without a
matching `X-CSRF-Token` value. Refresh the browser session or use bearer API-key
authentication for scripts.

`403 Forbidden`

The authenticated owner lacks the required RBAC permission at the requested
scope. Check role assignments for the user or service account, including parent
vault and project scopes.

`429 Too Many Requests`

The in-process REST rate limiter rejected the request. Wait for the reset window
and reduce script retry frequency. Health and metrics probes are exempt by
default.

Production startup fails with a configuration error

Run `make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production` and correct
the named variable. Do not weaken production safety toggles to make startup pass.

## Related Documentation

- `README.md` covers repository setup and local development entry points.
- `docs/USER_GUIDE.md` covers end-user browser and MCP workflows.
- `docs/BACKUP_GUIDE.md` is the top-level backup entry point.
- `backend/docs/BOOTSTRAP.md` documents system data bootstrap.
- `backend/docs/ENVIRONMENT.md` documents runtime environment variables.
- `backend/docs/DEPLOYMENT.md` covers production runtime configuration.
- `backend/docs/ROTATION_STRATEGY.md` covers credential rotation.
- `backend/docs/DISASTER_RECOVERY.md` covers restore and disaster recovery.
- `backend/docs/API_SPEC.md` and `backend/docs/MCP_SPEC.md` describe the
  intended REST and MCP contracts.
