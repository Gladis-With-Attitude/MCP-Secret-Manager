# System Data Bootstrap

The system data bootstrap makes a fresh local installation usable after:

```bash
docker compose up
```

It is an infrastructure concern and lives outside REST routes and business use
cases.

## Runtime Order

The local Compose stack starts services in this order:

1. `postgres`
2. `migrations`
3. `bootstrap`
4. `backend`
5. `frontend`

The `bootstrap` service runs once and exits. The backend starts only after the
bootstrap completed successfully.

## Seed Registry

Seeds are registered in `backend/src/infrastructure/seed/orchestrator.py` and
run in this order:

1. `PermissionsSeed`
2. `RolesSeed`
3. `AdminSeed`
4. `AdminApiKeySeed`
5. `ServiceAccountSeed`

Each seed is independent, idempotent and safe to replay.

## Data Created

The bootstrap creates or updates only system data:

- default permissions from the RBAC domain model;
- default roles: `administrator`, `user`, `readonly`;
- the configured administrator user;
- the administrator global role assignment;
- an optional administrator API key when explicitly configured;
- an optional service account when explicitly configured.

The bootstrap does not create Vaults, Projects, Secrets or any other business
resource.

## Environment Variables

```bash
MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED=true
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_EMAIL=admin@example.local
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_NAME=Administrator
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD=
MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY=
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_ENABLED=false
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_PROJECT_ID=
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_NAME=
MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_API_KEY=
```

`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_API_KEY` and
`MCP_SECRET_MANAGER_BOOTSTRAP_SERVICE_ACCOUNT_API_KEY` must never contain real
production secrets in committed files. When provided, raw API keys are hashed
before storage and never written to logs.

Password authentication is not implemented in the current runtime.
`MCP_SECRET_MANAGER_BOOTSTRAP_ADMIN_PASSWORD` is accepted as reserved
configuration but is not persisted until that authentication flow exists.

## Replaying Seeds

Run the bootstrap manually on an already migrated database:

```bash
make seed-run
```

Disable automatic bootstrap when needed:

```bash
MCP_SECRET_MANAGER_BOOTSTRAP_ENABLED=false docker compose up
```

## Failure Behavior

The bootstrap fails fast when required configuration is invalid or when an
optional service account references a project that does not exist. In that case,
Compose does not start the backend.
