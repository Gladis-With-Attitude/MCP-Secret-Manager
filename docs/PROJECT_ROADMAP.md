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
- Secret scanning ✅
- Dependency scanning ✅

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

Secret scanning adds a dedicated Gitleaks CI job that scans repository history
on pull requests, manual runs and pushes to `main` or
`security/production-readiness`. The same scanner can be run locally with
`make secret-scan`.

Dependency scanning adds a dedicated CI job for backend and frontend dependency
advisories on pull requests, manual runs and pushes to `main` or
`security/production-readiness`. Backend dependencies are audited with
`pip-audit` through uv, frontend dependencies are audited with `npm audit`, and
the same checks can be run locally with `make dependency-scan`.

### D3 - CI/CD

| Slice | Status | Scope |
| --- | --- | --- |
| D3a | ✅ | GitHub Actions quality gates for Ruff, MyPy, Pytest, frontend lint/typecheck/tests and frontend production build |
| D3b | ✅ | CI and local validation for backend and frontend Docker image builds |
| D3c | ✅ | Playwright end-to-end workflow checks |
| D3d | ✅ | Release pipeline |

D3b adds a dedicated GitHub Actions Docker build job for the backend and
frontend development images. The same validation can be run locally with
`make docker-build`.

D3c adds a dedicated Playwright CI job and local `make playwright-e2e` target
for a real browser workflow against the REST-backed frontend. The scenario
boots a migrated and bootstrapped test backend, signs in with an administrator
API key, creates vault/project/secret metadata, rotates and reveals a secret
value, creates and revokes an API key, creates a custom role, checks audit logs
and logs out.

D3d adds a release workflow for manual release-candidate runs and `v*` tag
pushes. The workflow reuses the existing CI gates, builds a source release
bundle through the local `make release-artifacts` target, uploads the bundle as a
workflow artifact and prepares draft GitHub Releases for tags only. It does not
publish container images or require deployment secrets.

### D4 - Deployment

| Slice | Status | Scope |
| --- | --- | --- |
| D4a | ✅ | Production backend and frontend Docker targets with multi-stage builds, non-root runtime users and container health checks |
| D4b | ✅ | Deployment readiness command for production backend/frontend environment validation, with unit coverage and CI gate |

D4a keeps the existing development Compose targets unchanged and adds dedicated
production image targets for backend and frontend. Local and CI validation can
build the hardened targets with `make docker-build-production`.

D4b adds `make deployment-readiness DEPLOYMENT_ENV_FILE=.env.production` for
local deployment checks. The command validates backend production security
configuration and frontend public build variables from an env file, reports only
safe metadata and is exercised by CI with a non-secret synthetic production env.

### D5 - Backup & Recovery

| Slice | Status | Scope |
| --- | --- | --- |
| D5a | ✅ | Local PostgreSQL backup and restore operator foundation |
| D5b | ✅ | Recovery tests |
| D5c | ✅ | Rotation strategy |
| D5d | ✅ | Disaster recovery documentation |

D5a adds Makefile targets and operator scripts for custom-format PostgreSQL
backups and guarded restores through the existing Compose database service. It
includes checksum generation, restricted local file permissions and initial
documentation for keeping database dumps separate from application master keys.

D5b adds automated recovery workflow coverage for the PostgreSQL backup and
restore scripts using a fake Compose command. The tests validate dump,
checksum, permission, cleanup, restore-streaming and restore-confirmation
behavior without requiring Docker or an external PostgreSQL service.

D5c adds the operational rotation strategy for stored secret values, API keys,
runtime signing secrets, PostgreSQL credentials, backup access and the
application master key. It links planned and incident-driven rotations to
pre-rotation backups, checksum verification, recovery channels, post-rotation
validation and master-key replacement limits in the current single-active-key
runtime.

D5d adds an operational disaster recovery runbook covering backup handling,
checksum verification, restore decision gates, post-restore validation,
separation of PostgreSQL dumps from the application master key and compromise
scenarios.

### D6 - Documentation

| Slice | Status | Scope |
| --- | --- | --- |
| D6a | ✅ | Top-level Backup Guide for operator backup handling and recovery links |
| D6b | ✅ | User Guide |
| D6c | ✅ | Administrator Guide |
| D6d | ✅ | Installation Guide |
| D6e | ⏳ | Deployment Guide consolidation |
| D6f | ⏳ | Upgrade Guide |
| D6g | ⏳ | Troubleshooting Guide |
| D6h | ⏳ | API Documentation |

D6a adds `docs/BACKUP_GUIDE.md` as the operator-facing backup entry point. It
summarizes the D5 PostgreSQL backup tooling, sensitive artifact handling,
checksum verification, restore readiness, master-key separation and links to
the disaster recovery and rotation runbooks.

D6b adds `docs/USER_GUIDE.md` as the concrete end-user entry point. It covers
sign-in and sessions, UI navigation, vault/project/secret workflows, secret
versions and rotation, API keys, MCP client usage, audit review, profile and
security settings, common errors and safe handling expectations.

D6c adds `docs/ADMINISTRATOR_GUIDE.md` as the administrator and operator entry
point. It covers bootstrap, administrator access, RBAC, API keys, service
accounts, audit review, production security controls, observability, backup and
restore coordination, rotation links and routine operator checks.

D6d adds `docs/INSTALLATION_GUIDE.md` as the local installation entry point. It
covers Docker Compose prerequisites, source checkout, local environment setup,
stack startup, first sign-in expectations, common local operations, smoke
validation, production configuration boundaries and links to administration,
backup and deployment references.

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
