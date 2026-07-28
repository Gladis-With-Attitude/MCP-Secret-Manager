# Playwright API E2E Tests

The C1 Playwright suite exercises the complete product workflow against a real REST backend. It does
not mock business data.

## Prerequisites

- A running backend with PostgreSQL migrations and bootstrap data applied.
- A bootstrap API key with permissions for vaults, projects, secrets, secret value decrypt/rotate,
  API keys, audit logs, and RBAC role management.

## Run

```bash
E2E_BOOTSTRAP_API_KEY="mcp_sm_..." \
E2E_API_BASE_URL="http://127.0.0.1:8000" \
npm run test:e2e
```
