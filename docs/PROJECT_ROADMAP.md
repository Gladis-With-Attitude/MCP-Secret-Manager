# MCP Secret Manager Project Roadmap

This document is the project reference roadmap for making MCP Secret Manager
ready to use on the target server.

The roadmap focuses on end-to-end usability first, then complete validation,
production hardening and release. A feature is not considered complete until it
works across the full path:

```text
Frontend -> REST API -> Use Cases -> PostgreSQL -> Frontend
```

## Status Legend

- ✅ Done
- 🔄 In progress
- ⏳ Planned

## Phase B - End-to-End Integration

Objective: make every core feature usable end to end.

| ID | Status | Scope |
| --- | --- | --- |
| B1 | ✅ | Vault End-to-End Integration |
| B2 | ✅ | Project End-to-End Integration |
| B3 | ✅ | Secret End-to-End Integration |
| B4 | ✅ | Secret Version End-to-End Integration |
| B5 | ✅ | Authentication & Session End-to-End Integration |
| B6 | ✅ | API Keys End-to-End Integration |
| B7 | ✅ | RBAC End-to-End Integration |
| B8 | ✅ | Profile & Settings End-to-End Integration |
| B9 | ✅ | Audit End-to-End Integration |

### Phase B Acceptance Rules

Each Phase B item must provide:

- frontend screens or flows connected to real backend data;
- REST endpoints wired to application use cases;
- persistence through PostgreSQL repositories and migrations when needed;
- error handling for validation, authentication and permissions;
- focused backend and frontend tests for the integrated behavior;
- no mocked business data in the final user-facing flow.

## Phase C - Complete System Validation

Objective: validate the product as a complete system once all features are
connected.

### C1 - Complete End-to-End Test Suite

Create complete scenarios covering:

- Login
- Vault creation
- Project creation
- Secret creation
- Secret rotation
- Secret read
- API key creation
- API key revocation
- Audit log verification
- Role management
- Logout

Required technologies:

- Playwright
- API tests
- Integration tests

### C2 - API Contract Validation

Objectives:

- verify that the frontend matches the OpenAPI contract exactly;
- detect contract regressions;
- generate clients if useful;
- add contract tests.

### C3 - Performance Validation

Test:

- pagination;
- search;
- audit queries;
- secret operations;
- API key operations;
- concurrent users.

### C4 - Security Validation

Test in particular:

- RBAC matrix;
- forbidden access;
- token leakage;
- secret leakage;
- authentication bypass;
- rate limiting;
- permission errors.

## Phase D - Production Hardening

Objective: transform the MVP into a production-ready product.

### D0 - Security Readiness Slices

| ID | Status | Scope |
| --- | --- | --- |
| S1 | ✅ | REST RBAC enforcement for protected resources |
| S2 | ✅ | Metadata-only bulk secret contracts and explicit `secret.decrypt` value access across REST/MCP |

### D1 - Observability

| Slice | Status | Scope |
| --- | --- | --- |
| D1a | ✅ | REST request IDs, safe structured logging helpers, HTTP request logs and lightweight Prometheus-compatible request metrics |
| D1b | ✅ | Prometheus scrape configuration, opt-in Compose service wiring and operator documentation for `/v1/metrics` |
| D1c | ✅ | Expanded application/service logs for high-value use cases |
| D1d | ✅ | Grafana dashboards |
| D1e | ✅ | OpenTelemetry traces and cross-service correlation |

D1a intentionally keeps the foundation small: logs and metrics include request
metadata such as method, route template, status, duration and request id, but do
not include request bodies, authorization headers, API keys or secret values.

D1b makes the existing lightweight `/v1/metrics` endpoint operationally
discoverable through checked-in Prometheus configuration and an opt-in local
Compose profile. It does not add Grafana dashboards, broader application logs or
OpenTelemetry tracing.

D1c expands safe structured application logs across high-value lifecycle,
credential, session and RBAC paths. The logs use resource identifiers, actor or
owner identifiers, counts and configuration booleans, and continue to avoid
request bodies, authorization headers, API keys, key prefixes, session tokens,
secret values, names and descriptions.

D1d adds opt-in Grafana provisioning and a checked-in dashboard for the existing
Prometheus metrics. The dashboard remains limited to aggregate REST request
counts, status codes and average duration.

D1e adds opt-in OpenTelemetry REST tracing with trace propagation and safe span
attributes for method, route template, status and request id. Tracing remains
disabled by default and excludes request bodies, authorization headers, API
keys, session tokens and secret material.

### D2 - Security Hardening

- D2a ✅ FastAPI baseline security headers and runtime-configured strict CORS
- D2b ✅ CSRF protection for HTTP-only session-cookie authentication
- D2c ✅ In-process REST rate limiting
- Secret scanning
- Dependency scanning

D2a applies baseline HTTP security headers to REST responses and wires FastAPI
CORS middleware to the existing runtime allow-list. Production validation keeps
security headers enabled, requires HTTPS CORS origins and rejects wildcard
origins.

D2b protects unsafe REST requests authenticated by the `mcp_sm_session`
HTTP-only cookie with a double-submit CSRF token: the backend issues a readable
`mcp_sm_csrf` cookie and requires the same value in `X-CSRF-Token`. Bearer API
key requests and safe methods keep their existing behavior.

D2c adds configurable in-process REST rate limiting keyed by direct client
address. The first slice intentionally avoids external storage; it exposes
standard rate-limit headers, rejects excess requests with `429`, exempts health
and metrics probes by default, and requires the limiter to stay enabled in
production configuration.

### D3 - CI/CD

- GitHub Actions
- Ruff
- MyPy
- Pytest
- Frontend tests
- Playwright
- Docker build
- Release pipeline

### D4 - Deployment

- Production Dockerfiles
- Multi-stage builds
- Non-root containers
- Health checks
- Readiness checks
- Environment validation

### D5 - Backup & Recovery

- PostgreSQL backups
- Restore procedure
- Recovery tests
- Rotation strategy
- Disaster recovery documentation

### D6 - Documentation

Complete:

- User Guide
- Administrator Guide
- Installation Guide
- Deployment Guide
- Backup Guide
- Upgrade Guide
- Troubleshooting Guide
- API Documentation

### D7 - Accessibility & UX

- WCAG 2.2 AA
- Keyboard navigation audit
- Screen readers
- Contrast validation
- Responsive audit

### D8 - Performance Optimisation

- Code splitting
- Lazy loading
- Bundle optimisation
- Query optimisation
- Cache optimisation
- Images
- Fonts

## Phase E - Release

Objective: complete the final step before v1.0.

### E1 - Release Candidate

- Feature freeze
- Bug fixes
- Code cleanup
- Security review
- Documentation review

### E2 - Version 1.0

- Git tag
- Changelog
- Release notes
- Docker images
- Publication
- Final documentation
