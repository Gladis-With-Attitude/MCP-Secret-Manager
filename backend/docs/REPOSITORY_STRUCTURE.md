# Repository Structure

This document defines the official repository organization for MCP Secret Manager.

It specifies where project artifacts should live, how source code should be grouped, how tests should be organized, how Docker services are orchestrated, and which structures are forbidden because they would violate the project's architecture.

This document does not define implementation code. It defines repository governance.

## Objectives

A clear repository structure is important because MCP Secret Manager is a security-sensitive, AI-first, MCP-native project.

The repository must remain understandable for:

- maintainers ;
- new contributors ;
- AI assistants ;
- security reviewers ;
- future OpenClaw integrations ;
- future SDK authors ;
- future operators.

The structure must support:

- readability ;
- separation of responsibilities ;
- evolvability ;
- onboarding ;
- AI-friendly navigation ;
- consistency with Clean Architecture ;
- clear security boundaries ;
- reliable reviews ;
- predictable testing.

The repository should make it obvious where a change belongs.

If a contributor cannot tell where to add a feature, the structure has failed.

## Principles

### One responsibility per directory

Each top-level directory must have a clear responsibility.

A directory should not mix unrelated concerns such as source code, documentation, migrations, generated artifacts and operational scripts.

### No business logic in infrastructure

Infrastructure code may persist data, call external services or implement technical details.

It must not own domain rules, authorization policy, secret lifecycle decisions or audit semantics.

### Separate Domain, Application, Infrastructure and Presentation

The source layout must reflect Clean Architecture:

- Domain defines core concepts and invariants ;
- Application orchestrates use cases ;
- Infrastructure implements technical details ;
- Presentation exposes interfaces.

Dependencies must point inward.

### Documentation separate from code

Backend documentation lives under `backend/docs/`.

Frontend documentation lives under `frontend/docs/`.

Repository-level documentation may live at the repository root when it describes the whole monorepo.

Documentation is not an afterthought. It is a source of truth and must remain versioned with the repository.

### Tests separate from code

Backend tests live under `backend/tests/`.

Frontend tests live under `frontend/tests/`.

Tests may mirror the source structure, but they should remain clearly separated from production code.

### Scripts separate from application logic

Backend operational and developer scripts live under `backend/scripts/`.

Repository-level orchestration scripts may live at the repository root when they coordinate several services.

Scripts must not become hidden application behavior.

### Migrations separate from source code

Database migrations live under `db/migrations/`.

Migrations are part of the persistence lifecycle and must be visible, reviewable and testable.

## Repository Layout

The repository is a Docker-oriented monorepo. The root coordinates services and shared project governance; application code lives in dedicated service directories.

### Root

Purpose:

Repository-level orchestration and cross-service documentation.

Contains:

- `docker-compose.yml` ;
- root `Makefile` ;
- root `README.md` ;
- root `.env.example` without real secrets ;
- repository-level ignore and editor configuration ;
- CI configuration when introduced.

Does not contain:

- backend source code ;
- frontend source code ;
- database migrations ;
- service-specific dependencies ;
- generated build artifacts ;
- real secrets.

### `backend/`

Purpose:

FastAPI backend service.

Contains:

- `backend/src/` ;
- `backend/tests/` ;
- `backend/docs/` ;
- `backend/configs/` ;
- `backend/scripts/` ;
- `backend/examples/` ;
- `backend/tools/` ;
- backend dependency and tooling files ;
- `backend/Dockerfile`.

Does not contain:

- frontend source code ;
- PostgreSQL migration source of truth ;
- root orchestration files ;
- local secrets.

### `frontend/`

Purpose:

Next.js frontend service.

Contains:

- `frontend/app/` ;
- `frontend/features/` ;
- `frontend/components/` ;
- `frontend/providers/` ;
- `frontend/lib/` ;
- `frontend/hooks/` ;
- `frontend/config/` ;
- `frontend/styles/` ;
- `frontend/assets/` ;
- `frontend/types/` ;
- `frontend/tests/` ;
- `frontend/docs/` ;
- frontend dependency and tooling files ;
- `frontend/Dockerfile`.

Does not contain:

- backend business logic ;
- backend DTOs as implementation source ;
- database migrations ;
- secrets or credentials.

### `db/`

Purpose:

Database migration assets and database-specific documentation.

Contains:

- `db/migrations/` ;
- `db/alembic.ini` ;
- `db/config/` for future non-secret database configuration templates ;
- `db/README.md`.

Does not contain:

- ORM models ;
- backend repositories ;
- frontend code ;
- business rules ;
- seed secrets ;
- plaintext secret values.

### `backend/configs/`

Purpose:

Backend configuration templates and non-secret examples.

Contains:

- example configuration ;
- environment templates ;
- local development configuration samples ;
- production configuration templates without secrets.

Does not contain:

- real tokens ;
- real API keys ;
- master keys ;
- private keys ;
- environment files containing secrets.

### `backend/examples/`

Purpose:

Safe examples showing how to use MCP Secret Manager.

Contains:

- example API usage descriptions ;
- example MCP workflows ;
- example OpenClaw integration scenarios ;
- example configuration patterns without secrets.

Does not contain:

- production credentials ;
- real external provider secrets ;
- required application logic.

### `backend/tools/`

Purpose:

Repository tooling that supports development, validation or documentation.

Contains:

- developer tooling ;
- documentation tooling ;
- static analysis helpers ;
- generation helpers if introduced later.

Does not contain:

- runtime application code ;
- business logic ;
- security policy ;
- hidden deployment behavior.

## Source Layout

The `backend/src/` directory is organized around Clean Architecture.

### `backend/src/presentation/`

Responsibilities:

- expose external interfaces ;
- receive external requests ;
- validate protocol-level input ;
- translate requests into application commands ;
- translate application responses into protocol responses.

Allowed:

- REST adapter ;
- MCP adapter ;
- CLI adapter ;
- protocol-specific request and response mapping ;
- protocol-specific error mapping.

Forbidden:

- business authorization logic ;
- direct PostgreSQL access ;
- direct decryption ;
- domain rule implementation ;
- duplicated secret lifecycle workflows ;
- MCP depending on REST ;
- REST depending on MCP.

### `backend/src/application/`

Responsibilities:

- orchestrate use cases ;
- coordinate permissions ;
- coordinate secret lifecycle operations ;
- invoke crypto only after authorization ;
- invoke audit for sensitive actions ;
- coordinate repositories through abstractions.

Allowed:

- use cases ;
- application services ;
- repository contracts ;
- authorization orchestration ;
- transaction-level workflow definitions ;
- audit coordination.

Forbidden:

- FastAPI-specific code ;
- MCP protocol details ;
- CLI parsing ;
- raw SQL ;
- concrete PostgreSQL implementation ;
- concrete cryptographic library details.

### `backend/src/domain/`

Responsibilities:

- define core business concepts ;
- define valid states ;
- enforce domain invariants ;
- represent entities and value concepts ;
- remain independent of frameworks.

Allowed:

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- SecretProvider ;
- Actor ;
- Role ;
- Permission ;
- Token concepts ;
- AuditEvent concepts ;
- domain errors ;
- domain invariants.

Forbidden:

- FastAPI ;
- MCP SDK concepts ;
- PostgreSQL ;
- SQLAlchemy ;
- Docker ;
- concrete crypto library calls ;
- environment configuration ;
- infrastructure dependencies.

### `backend/src/infrastructure/`

Responsibilities:

- implement persistence ;
- implement cryptographic operations ;
- implement configuration loading ;
- implement token storage ;
- implement audit storage ;
- integrate external technical systems.

Allowed:

- PostgreSQL repositories ;
- migration integration ;
- crypto backend implementation ;
- configuration loading ;
- health check dependencies ;
- provider adapters ;
- logging infrastructure.

Forbidden:

- ownership of business rules ;
- authorization decisions ;
- direct protocol behavior ;
- hidden secret lifecycle rules ;
- audit semantics that contradict Application Layer ;
- storing plaintext secrets.

### `backend/src/shared/`

Responsibilities:

- host small shared technical utilities that do not belong to a domain module ;
- provide generic helpers with no business ownership.

Allowed:

- generic result or error helpers ;
- typing helpers ;
- small framework-independent utilities ;
- constants that are not domain policy.

Forbidden:

- becoming a dumping ground ;
- business logic ;
- security policy ;
- domain entities ;
- infrastructure shortcuts ;
- cross-layer coupling.

`shared/` must stay small. If it grows, the design should be reconsidered.

## Documentation Layout

### `backend/docs/`

The backend documentation directory contains official backend project documents.

Examples:

- project vision ;
- constitution ;
- architecture ;
- security ;
- database model ;
- cryptography ;
- API specification ;
- MCP specification ;
- testing strategy ;
- AI governance ;
- contribution guide ;
- repository structure.

### `backend/docs/adr/`

Contains Architecture Decision Records.

ADR files must:

- have a stable number ;
- have a descriptive slug ;
- use the accepted ADR format ;
- document context, decision, alternatives, consequences and future evolution.

### Future docs

Future documentation may include:

- operator guides ;
- deployment guides ;
- OpenClaw integration guide ;
- CLI guide ;
- SDK guides ;
- provider guides ;
- incident response playbooks ;
- release process ;
- security disclosure policy.

Future docs must not contradict existing foundational documents without an explicit update.

### Architecture docs

Architecture documentation should explain:

- layers ;
- dependencies ;
- modules ;
- boundaries ;
- invariants ;
- ADR relationships.

### API docs

API documentation should explain:

- REST resources ;
- conceptual endpoints ;
- authentication ;
- authorization ;
- errors ;
- pagination ;
- compatibility.

### Security docs

Security documentation should explain:

- threat model ;
- cryptography ;
- audit ;
- production hardening ;
- incident response ;
- release checklist.

## Test Layout

The `backend/tests/` directory is organized by test intent.

### `backend/tests/unit/`

Purpose:

Fast, isolated tests for domain and application logic.

Expected coverage:

- permissions ;
- domain invariants ;
- secret lifecycle ;
- audit event construction ;
- crypto-facing contracts with test doubles.

### `backend/tests/integration/`

Purpose:

Tests involving multiple components and controlled infrastructure.

Expected coverage:

- PostgreSQL repositories ;
- migrations applied to a real test database ;
- persistence and retrieval ;
- audit persistence ;
- token persistence.

### `backend/tests/e2e/`

Purpose:

End-to-end workflows.

Expected coverage:

- OpenClaw-style service account flow ;
- create vault ;
- create project ;
- create secret ;
- read via REST ;
- read via MCP ;
- verify audit.

### `backend/tests/security/`

Purpose:

Security-specific behavior.

Expected coverage:

- RBAC denial ;
- vault locked ;
- no secret in logs ;
- no secret in errors ;
- no secret in audit ;
- token revoked ;
- malformed MCP calls ;
- crypto failure behavior.

### `backend/tests/fixtures/`

Purpose:

Reusable safe test data.

Rules:

- no real secrets ;
- no production credentials ;
- no real API keys ;
- deterministic data ;
- clear naming.

### Test utilities

Test utilities may exist under a clearly named test support area.

They must:

- stay test-only ;
- not become production dependencies ;
- avoid hidden network calls ;
- avoid real secrets.

## Configuration Layout

### Configuration

Backend configuration templates live under `backend/configs/`.

Runtime configuration loading belongs in `backend/src/infrastructure/`.

Configuration examples must never contain real secrets.

### Environment examples

Environment examples may live under `backend/configs/`.

They must:

- use placeholder values ;
- clearly indicate non-production status ;
- avoid real credentials.

### Docker files

Docker Compose orchestration lives at the repository root in `docker-compose.yml`.

Service Dockerfiles live with their services:

- `backend/Dockerfile` ;
- `frontend/Dockerfile`.

Docker ignore files may exist at the root and inside service directories to keep build contexts small and free of generated artifacts.

Docker files must not contain embedded secrets.

### CI configuration

CI configuration may live in the platform-required location.

Examples:

- GitHub Actions under `.github/` if GitHub is used ;
- other CI-specific directories if another platform is used.

CI must remain aligned with `backend/docs/TESTING.md` and frontend testing documentation.

### Lint

Lint configuration may live at the repository root or in tool-specific configuration files.

It must be documented when introduced.

### Formatters

Formatter configuration may live at the repository root.

Formatting rules must support readability and stable diffs.

## Naming Conventions

### Directories

Directory names should be:

- lowercase ;
- explicit ;
- stable ;
- responsibility-oriented.

Avoid vague names such as `misc`, `stuff`, `common` or `new`.

### Files

File names should be:

- descriptive ;
- consistent ;
- easy to search ;
- aligned with their module responsibility.

### ADRs

ADR files use the format:

```text
ADR-0000-short-description.md
```

Rules:

- four-digit number ;
- stable sequence ;
- lowercase slug ;
- hyphen-separated words ;
- no renumbering after acceptance.

### Documentation

Foundational documentation uses uppercase names when it represents a project-level reference document.

Examples:

- `backend/docs/PROJECT.md` ;
- `backend/docs/SECURITY.md` ;
- `backend/docs/DATABASE.md`.

Specialized guides may use descriptive names.

### Modules

Module names should reflect domain or architectural responsibility.

Good module names:

- `auth` ;
- `vault` ;
- `secret` ;
- `permissions` ;
- `audit` ;
- `crypto` ;
- `mcp` ;
- `rest`.

Avoid names based only on frameworks or temporary implementation details.

## Forbidden Structures

The following structures are forbidden because they violate the architecture or make security review harder.

### Framework-centric source root

Forbidden pattern:

- all application logic organized around web framework files ;
- business rules inside route handlers ;
- permissions inside controllers.

Why forbidden:

It makes the framework the architecture and hides security logic in protocol code.

### REST and MCP as separate applications with duplicated business logic

Forbidden pattern:

- REST implements one version of secret reading ;
- MCP implements another version of secret reading ;
- each interface checks permissions differently.

Why forbidden:

It creates divergence in authorization, audit and crypto sequencing.

### Infrastructure owning business rules

Forbidden pattern:

- repositories decide whether a secret can be read ;
- database queries encode business authorization ;
- crypto implementation decides access rights.

Why forbidden:

Business rules belong in Domain and Application layers, not Infrastructure.

### Domain depending on frameworks

Forbidden pattern:

- Domain imports FastAPI ;
- Domain imports MCP protocol types ;
- Domain imports PostgreSQL-specific code.

Why forbidden:

It violates Clean Architecture and makes the core model non-portable.

### Shared dumping ground

Forbidden pattern:

- large `shared`, `common` or `utils` area containing unrelated logic ;
- domain concepts mixed with infrastructure helpers ;
- security helpers used across layers without clear ownership.

Why forbidden:

It hides responsibility and encourages coupling.

### Tests mixed with production code

Forbidden pattern:

- test-only fixtures inside production modules ;
- production code depending on test utilities.

Why forbidden:

It weakens boundaries and can accidentally introduce unsafe test behavior into runtime.

### Secrets in configuration examples

Forbidden pattern:

- real tokens ;
- real API keys ;
- real private keys ;
- realistic credentials committed for convenience.

Why forbidden:

The repository must never contain real secrets.

## Related Documents

- `backend/docs/PROJECT.md`
- `backend/docs/CONSTITUTION.md`
- `backend/docs/ARCHITECTURE.md`
- `backend/docs/SECURITY.md`
- `backend/docs/DATABASE.md`
- `backend/docs/CRYPTOGRAPHY.md`
- `backend/docs/API_SPEC.md`
- `backend/docs/MCP_SPEC.md`
- `backend/docs/TESTING.md`
- `backend/docs/AI_RULES.md`
- `backend/docs/CONTRIBUTING.md`
- `backend/docs/adr/ADR-0001-clean-architecture.md`
- `backend/docs/adr/ADR-0002-postgresql-primary-storage.md`
- `backend/docs/adr/ADR-0003-envelope-encryption.md`
- `backend/docs/adr/ADR-0004-rest-mcp-dual-interface.md`
- `backend/docs/adr/ADR-0005-rbac-authorization-model.md`
- `backend/docs/adr/ADR-0006-documentation-first-development.md`
- `backend/docs/adr/ADR-0007-openclaw-first-mvp.md`
- `backend/docs/adr/ADR-0008-ai-first-governance.md`

## Future Evolution

The repository structure may evolve as the project grows.

Possible future additions:

- SDK directories ;
- Web UI directory ;
- deployment directory ;
- packaging directory ;
- provider-specific integration directories ;
- benchmark directory ;
- fuzzing directory ;
- security disclosure documents ;
- release process documents.

Any evolution must:

- preserve Clean Architecture ;
- keep documentation versioned ;
- keep tests separate from production code ;
- keep migrations visible ;
- avoid framework-centric organization ;
- avoid client-specific coupling ;
- preserve REST and MCP as independent adapters ;
- remain understandable to humans and AI assistants.

If a structural change affects architecture, governance, security boundaries or public contribution workflow, it should be documented in an ADR.
