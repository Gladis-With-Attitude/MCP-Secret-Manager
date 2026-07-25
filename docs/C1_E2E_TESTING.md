# C1 End-to-End Test Suite

Phase C1 is covered by two complementary suites:

- `backend/tests/integration/rest/test_complete_e2e_flow.py` drives the REST API through login,
  vault creation, project creation, secret creation, secret rotation, secret read, API key creation,
  API key revocation, audit verification, role management, and logout against PostgreSQL.
- `frontend/e2e/complete-product-workflow.spec.ts` drives the same product workflow with
  Playwright's API client against a real backend.

## Backend Integration E2E

Run from `backend/` with a PostgreSQL test database URL:

```bash
MCP_SECRET_MANAGER_TEST_DATABASE_URL="postgresql+asyncpg://user:password@127.0.0.1:5432/mcp_secret_manager" \
uv run --extra dev python -m pytest tests/integration/rest/test_complete_e2e_flow.py
```

The test creates and drops its own PostgreSQL schema.

## Playwright API E2E

Run from `frontend/` with a running backend:

```bash
npx playwright install chromium
E2E_BOOTSTRAP_API_KEY="mcp_sm_..." \
E2E_API_BASE_URL="http://127.0.0.1:8000" \
npm run test:e2e
```

The bootstrap API key must belong to an actor with permissions for vaults, projects, secrets,
secret value decrypt/rotate, API keys, audit logs, and RBAC role management.
