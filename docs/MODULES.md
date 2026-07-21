# Modules

This document defines the functional and architectural module boundaries of MCP Secret Manager.

It describes the responsibilities of each module, the entities they own, the use cases they support, their allowed dependencies and the patterns that are forbidden.

This document does not contain implementation code. It defines module governance.

## Objectives

Module boundaries are important because MCP Secret Manager is a security-sensitive, AI-first, MCP-native project.

The system must remain understandable as it grows from an OpenClaw-first MVP into a broader Secret Manager for MCP clients, agents, services, SDKs and future providers.

The module design aims to provide:

- separation of responsibilities ;
- low coupling ;
- high cohesion ;
- evolvability ;
- testability ;
- AI-friendly navigation ;
- easier reviews ;
- clearer ownership ;
- stronger security boundaries.

A contributor should be able to understand where a behavior belongs without reading the entire codebase.

An AI assistant should be able to locate the right module without inventing new structure.

## Principles

### One module equals one business responsibility

Each module should own one clear area of the domain or infrastructure-facing behavior.

Examples:

- Vault owns vault lifecycle ;
- Secret owns secret metadata lifecycle ;
- Secret Version owns version lifecycle ;
- Authorization owns RBAC decisions ;
- Audit owns audit events.

A module must not become a generic container for unrelated behavior.

### Communication through the Application Layer

Modules must be coordinated by the Application Layer.

The Application Layer orchestrates workflows such as reading a secret, creating a version or revoking a token.

Modules should not bypass the Application Layer to perform cross-module workflows.

### No circular dependencies

Circular dependencies are forbidden.

If two modules appear to require each other directly, the responsibility boundaries are wrong or the workflow belongs in the Application Layer.

### Explicit interfaces

Modules should expose explicit capabilities.

Implicit access to internal state creates coupling and makes security review harder.

Interfaces should make it clear:

- what operation is performed ;
- what input is required ;
- what decision is returned ;
- what errors are possible ;
- whether audit is required.

### Protocol-independent modules

Business modules must be independent of REST, MCP and CLI.

REST and MCP are Presentation Layer adapters.

Modules must not depend on protocol-specific request or response types.

## Module List

## Vault

### Responsibilities

The Vault module owns the lifecycle and state of vaults.

It represents the primary logical and cryptographic boundary of the system.

Responsibilities:

- create vaults ;
- read vault metadata ;
- update vault metadata ;
- lock vaults ;
- archive vaults ;
- enforce vault state invariants ;
- expose vault state to workflows.

### Entities

- Vault ;
- Vault state ;
- Vault metadata.

### Use cases

- create vault ;
- list vaults ;
- get vault ;
- update vault metadata ;
- lock vault ;
- archive vault ;
- verify vault is usable for a given operation.

### Allowed dependencies

- Domain concepts ;
- Application-level repository contracts ;
- Authorization through Application orchestration ;
- Audit through Application orchestration.

### Forbidden

- direct protocol handling ;
- direct PostgreSQL access from domain logic ;
- crypto implementation details ;
- secret value handling ;
- OpenClaw-specific logic ;
- bypassing Authorization for sensitive operations.

## Project

### Responsibilities

The Project module organizes secrets inside vaults.

Responsibilities:

- create projects ;
- list projects in a vault ;
- read project metadata ;
- update project metadata ;
- archive projects ;
- enforce project-vault relationship invariants.

### Entities

- Project ;
- Project metadata ;
- Project state.

### Use cases

- create project ;
- list projects ;
- get project ;
- update project ;
- archive project ;
- verify project belongs to vault.

### Allowed dependencies

- Domain concepts ;
- Vault state through Application orchestration ;
- Application-level repository contracts ;
- Authorization through Application orchestration ;
- Audit through Application orchestration.

### Forbidden

- storing secret values ;
- managing SecretVersion lifecycle ;
- direct REST or MCP behavior ;
- direct database implementation in domain logic ;
- OpenClaw-specific behavior.

## Secret

### Responsibilities

The Secret module owns the logical identity and metadata lifecycle of secrets.

Responsibilities:

- create secret metadata ;
- read secret metadata ;
- list secret metadata ;
- update secret metadata ;
- archive secrets ;
- delete secrets logically ;
- maintain the current version reference ;
- preserve metadata/value separation.

### Entities

- Secret ;
- Secret metadata ;
- Secret state ;
- current version reference.

### Use cases

- create secret ;
- list secrets ;
- get secret metadata ;
- update secret metadata ;
- archive secret ;
- delete secret logically ;
- resolve current version.

### Allowed dependencies

- Project through Application orchestration ;
- Provider metadata ;
- Secret Version through Application orchestration ;
- Authorization through Application orchestration ;
- Audit through Application orchestration.

### Forbidden

- direct decryption ;
- storing plaintext values ;
- deciding authorization ;
- protocol-specific behavior ;
- modifying existing SecretVersion values ;
- leaking value through metadata endpoints.

## Secret Version

### Responsibilities

The Secret Version module owns immutable versions of secret values.

Responsibilities:

- create a new secret version ;
- list version metadata ;
- read version metadata ;
- mark versions current according to use case rules ;
- support future revocation ;
- support future destruction states ;
- enforce immutability.

### Entities

- SecretVersion ;
- version state ;
- cryptographic metadata reference ;
- version number or identity.

### Use cases

- create initial version ;
- create new version ;
- list versions ;
- get version metadata ;
- read current version through Application workflow ;
- read explicit version through Application workflow ;
- future revoke version ;
- future destroy version.

### Allowed dependencies

- Secret through Application orchestration ;
- Crypto through Application orchestration ;
- Authorization through Application orchestration ;
- Audit through Application orchestration ;
- repository contracts.

### Forbidden

- modifying existing version value ;
- deciding whether an actor may read a value ;
- direct protocol response shaping ;
- plaintext persistence ;
- audit events containing values.

## Authentication

### Responsibilities

The Authentication module identifies the actor making a request.

Responsibilities:

- validate authentication material ;
- resolve actor identity ;
- distinguish human users, service accounts and future agents ;
- reject invalid or revoked credentials ;
- provide actor context to Application use cases.

### Entities

- Actor ;
- authentication context ;
- credential metadata ;
- future agent authentication context.

### Use cases

- authenticate request ;
- resolve actor ;
- reject invalid token ;
- reject disabled actor ;
- future authenticate agent identity.

### Allowed dependencies

- Token module ;
- Actor repository contracts ;
- configuration for authentication policy ;
- Audit through Application orchestration for sensitive events.

### Forbidden

- deciding resource authorization ;
- granting permissions implicitly ;
- reading secret values ;
- protocol-specific business behavior ;
- storing raw token values in logs.

## Authorization (RBAC)

### Responsibilities

The Authorization module owns RBAC decisions.

Responsibilities:

- resolve roles for an actor ;
- resolve permissions for roles ;
- evaluate whether an action is allowed ;
- deny by default ;
- keep REST and MCP decisions consistent ;
- expose explicit authorization decisions.

### Entities

- Role ;
- Permission ;
- ActorRole ;
- RolePermission ;
- authorization decision ;
- resource reference.

### Use cases

- check permission ;
- list roles ;
- list permissions ;
- assign role ;
- revoke role ;
- create role ;
- update role.

### Allowed dependencies

- Actor identity ;
- Role and Permission repository contracts ;
- resource identifiers ;
- Audit through Application orchestration.

### Forbidden

- depending on decrypted secret values ;
- calling Crypto ;
- protocol-specific authorization logic ;
- implicit wildcard behavior ;
- interface-specific decisions ;
- hidden allow behavior.

## Audit

### Responsibilities

The Audit module records security-relevant events.

Responsibilities:

- construct audit events ;
- persist audit events ;
- distinguish allowed and denied decisions ;
- record actor, action, resource and client type ;
- support audit queries ;
- ensure audit never contains secret values.

### Entities

- AuditEvent ;
- audit action ;
- audit decision ;
- audit resource reference ;
- client type.

### Use cases

- record event ;
- record allowed action ;
- record denied action ;
- list audit events ;
- filter audit events ;
- get audit event.

### Allowed dependencies

- Actor identity ;
- resource references ;
- repository contracts ;
- Application context.

### Forbidden

- receiving secret values ;
- storing token values ;
- deciding authorization ;
- triggering crypto ;
- becoming a business data store ;
- exposing audit without permission.

## Crypto

### Responsibilities

The Crypto module provides cryptographic capabilities.

Responsibilities:

- encrypt secret values ;
- decrypt authorized secret values ;
- manage cryptographic metadata ;
- support envelope encryption ;
- support future key rotation ;
- support future rewrap ;
- enforce cryptographic invariants.

### Entities

- cryptographic metadata ;
- key references ;
- algorithm identifiers ;
- wrapped key material references ;
- encryption context.

### Use cases

- encrypt new secret version ;
- decrypt secret version after authorization ;
- validate cryptographic metadata ;
- future rotate DEK ;
- future rewrap ;
- future rotate master key.

### Allowed dependencies

- Infrastructure crypto backend ;
- configuration ;
- domain identifiers used as encryption context ;
- Application orchestration.

### Forbidden

- deciding permissions ;
- logging secret values ;
- writing AuditEvents directly ;
- depending on REST or MCP ;
- storing plaintext secrets ;
- implementing home-made cryptography.

## Tokens

### Responsibilities

The Tokens module owns token lifecycle.

Responsibilities:

- create tokens ;
- store token metadata ;
- validate token status ;
- revoke tokens ;
- ensure complete tokens are not stored in plaintext ;
- support future expiration and rotation.

### Entities

- Token ;
- token metadata ;
- token state ;
- token owner Actor.

### Use cases

- create token ;
- list token metadata ;
- get token metadata ;
- revoke token ;
- validate token ;
- future expire token ;
- future rotate token.

### Allowed dependencies

- Actor ;
- Authentication ;
- Authorization through Application orchestration ;
- Audit through Application orchestration ;
- repository contracts.

### Forbidden

- storing complete token values in plaintext ;
- granting permissions ;
- reading secret values ;
- protocol-specific behavior ;
- bypassing actor state checks.

## Service Accounts

### Responsibilities

The Service Accounts module owns non-human service identities.

Responsibilities:

- create service accounts ;
- associate service accounts with Actors ;
- represent OpenClaw as a service account ;
- disable service accounts ;
- support service-specific audit and token lifecycle.

### Entities

- ServiceAccount ;
- associated Actor ;
- service metadata ;
- service state.

### Use cases

- create service account ;
- get service account ;
- list service accounts ;
- disable service account ;
- create token for service account ;
- assign role to service account.

### Allowed dependencies

- Actor ;
- Tokens through Application orchestration ;
- Authorization through Application orchestration ;
- Audit through Application orchestration.

### Forbidden

- OpenClaw-specific domain rules ;
- implicit admin permissions ;
- direct secret access ;
- bypassing RBAC ;
- sharing identity with human users.

## Configuration

### Responsibilities

The Configuration module loads and validates runtime configuration.

Responsibilities:

- load configuration ;
- validate required settings ;
- reject unsafe production configuration ;
- expose configuration to infrastructure components ;
- support environment-specific configuration.

### Entities

- runtime configuration ;
- database configuration ;
- crypto configuration ;
- interface configuration ;
- security configuration.

### Use cases

- load configuration ;
- validate configuration ;
- expose safe settings ;
- fail startup on invalid critical configuration.

### Allowed dependencies

- Infrastructure ;
- environment ;
- configuration files ;
- startup composition.

### Forbidden

- business rules ;
- permission decisions ;
- secret value storage ;
- hidden defaults for production security ;
- logging sensitive configuration values.

## Health

### Responsibilities

The Health module reports service health.

Responsibilities:

- report liveness ;
- report readiness ;
- check critical dependencies ;
- avoid exposing sensitive information.

### Entities

- health status ;
- readiness status ;
- dependency status.

### Use cases

- liveness check ;
- readiness check ;
- database connectivity check ;
- configuration readiness check ;
- future dependency health checks.

### Allowed dependencies

- Infrastructure dependency probes ;
- configuration status ;
- database connectivity status.

### Forbidden

- exposing secrets ;
- exposing master key state in detail ;
- exposing sensitive configuration ;
- performing business operations ;
- bypassing authentication for detailed health if restricted.

## Providers

### Responsibilities

The Providers module owns the Secret Provider abstraction.

Responsibilities:

- define provider identity ;
- associate secrets with providers ;
- expose provider capabilities ;
- support local static provider in the MVP ;
- prepare future external providers.

### Entities

- SecretProvider ;
- provider capability ;
- provider metadata ;
- provider state.

### Use cases

- list providers ;
- get provider ;
- validate provider availability ;
- associate provider with secret ;
- future validate secret ;
- future rotate via provider ;
- future sync provider metadata.

### Allowed dependencies

- Secret through Application orchestration ;
- configuration for provider availability ;
- future external adapters through Infrastructure ;
- Authorization through Application orchestration ;
- Audit through Application orchestration.

### Forbidden

- bypassing RBAC ;
- bypassing Audit ;
- returning secret values without Secret workflows ;
- making external providers part of the Domain core ;
- coupling the core model to a specific provider.

## Module Interactions

Allowed interactions are coordinated by the Application Layer.

Conceptual view:

```text
             +----------------------+
             |    Presentation      |
             | REST / MCP / CLI     |
             +----------+-----------+
                        |
                        v
             +----------------------+
             |    Application       |
             | Use Case Workflows   |
             +----------+-----------+
                        |
     +------------------+------------------+
     |                  |                  |
     v                  v                  v
+---------+      +--------------+      +---------+
|  Auth   |      | Authorization|      |  Audit  |
+---------+      +--------------+      +---------+
     |                  |                  ^
     |                  |                  |
     v                  v                  |
+---------+      +--------------+          |
| Tokens  |      | Roles/Perms  |          |
+---------+      +--------------+          |
                        |                  |
                        v                  |
                +---------------+          |
                | Secret Flows  +----------+
                +-------+-------+
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      +-------+     +---------+   +---------+
      | Vault |     | Project |   | Secret  |
      +-------+     +---------+   +----+----+
                                      |
                                      v
                              +---------------+
                              | SecretVersion |
                              +-------+-------+
                                      |
                                      v
                                  +--------+
                                  | Crypto |
                                  +--------+
```

### Allowed interaction rules

- Presentation calls Application ;
- Application orchestrates modules ;
- Authorization may read Actor, Role and Permission data ;
- Authentication may use Tokens and Actors ;
- Secret workflows may use Vault, Project, Secret, Secret Version, Providers, Authorization, Crypto and Audit ;
- Crypto is called only after authorization ;
- Audit is called by Application workflows ;
- Providers are used through Secret workflows ;
- Infrastructure implements persistence and technical operations.

### Forbidden dependencies

- Domain must not depend on Infrastructure ;
- Domain must not depend on REST or MCP ;
- REST must not depend on MCP ;
- MCP must not depend on REST ;
- Crypto must not depend on Authorization ;
- Authorization must not depend on Crypto ;
- Audit must not depend on secret values ;
- Providers must not bypass Secret workflows ;
- OpenClaw must not be a module dependency ;
- modules must not create circular dependencies.

## Cross-Cutting Concerns

### Logging

Logging is cross-cutting but must remain controlled.

Rules:

- no secret values ;
- no complete tokens ;
- no master keys ;
- no sensitive payload dumps ;
- logs should carry request identifiers and safe context.

Logging must not become a hidden communication channel between modules.

### Configuration

Configuration is loaded and validated centrally.

Modules should receive explicit configuration values or configuration objects appropriate to their responsibility.

Modules must not read arbitrary environment variables throughout the codebase.

### Audit

Audit is cross-cutting but not everywhere.

Application workflows decide when audit is required.

Modules should not independently write audit events unless explicitly designed to do so through the application workflow.

Audit must never receive secret values.

### Errors

Errors should be raised or returned close to their cause and transformed at boundaries.

Rules:

- domain errors stay protocol-independent ;
- application errors represent use case failures ;
- presentation maps errors to REST, MCP or CLI ;
- infrastructure errors are wrapped safely ;
- errors must not contain secrets.

### Transactions

Transactions are coordinated at the Application Layer.

Infrastructure provides transaction capabilities.

Business workflows decide transaction boundaries.

### Security

Security is cross-cutting but must not be scattered.

Rules:

- Authorization decisions are centralized ;
- Crypto is called only after authorization ;
- Audit records sensitive actions ;
- Presentation validates protocol input ;
- Domain enforces invariants ;
- Infrastructure must not bypass security workflows.

## Naming Rules

Module names should be:

- domain-oriented ;
- explicit ;
- lowercase in source layout ;
- stable ;
- searchable.

Good names:

- `vault` ;
- `project` ;
- `secret` ;
- `secret_version` ;
- `authentication` ;
- `authorization` ;
- `audit` ;
- `crypto` ;
- `tokens` ;
- `service_accounts` ;
- `configuration` ;
- `health` ;
- `providers`.

Avoid:

- `utils` as a business module ;
- `common` as a business module ;
- `manager` without a precise subject ;
- framework-specific names for domain modules ;
- client-specific module names for core behavior.

## Forbidden Patterns

### God Module

Forbidden:

A module that owns vaults, secrets, permissions, crypto and audit together.

Why forbidden:

It destroys separation of responsibilities and makes security review harder.

### Shared catch-all

Forbidden:

A `shared`, `common` or `utils` area containing unrelated business logic.

Why forbidden:

It hides ownership and creates coupling.

### Cycles

Forbidden:

Vault depends on Secret while Secret depends on Vault directly, or Authorization depends on Secret while Secret depends on Authorization directly.

Why forbidden:

Cycles make behavior hard to reason about and indicate misplaced orchestration.

### REST to business coupling

Forbidden:

REST handlers implementing secret lifecycle, permission checks or crypto sequencing directly.

Why forbidden:

Business workflows belong in the Application Layer.

### MCP to business coupling

Forbidden:

MCP tools implementing separate business logic from REST.

Why forbidden:

REST and MCP must share decisions through Application use cases.

### PostgreSQL to Domain coupling

Forbidden:

Domain entities depending on PostgreSQL, SQLAlchemy or table structure.

Why forbidden:

Domain must remain independent of persistence.

### OpenClaw to modules coupling

Forbidden:

Core modules containing OpenClaw-specific rules.

Why forbidden:

OpenClaw is the first MVP consumer, not an internal dependency.

## Related Documents

- `docs/ARCHITECTURE.md`
- `docs/DATABASE.md`
- `docs/SECURITY.md`
- `docs/API_SPEC.md`
- `docs/MCP_SPEC.md`
- `docs/REPOSITORY_STRUCTURE.md`
- `docs/adr/ADR-0001-clean-architecture.md`
- `docs/adr/ADR-0002-postgresql-primary-storage.md`
- `docs/adr/ADR-0003-envelope-encryption.md`
- `docs/adr/ADR-0004-rest-mcp-dual-interface.md`
- `docs/adr/ADR-0005-rbac-authorization-model.md`
- `docs/adr/ADR-0006-documentation-first-development.md`
- `docs/adr/ADR-0007-openclaw-first-mvp.md`
- `docs/adr/ADR-0008-ai-first-governance.md`

## Future Evolution

New modules may be added as the project grows.

Examples:

- Agent Identity ;
- Mission ;
- Quota ;
- Budget ;
- Rotation ;
- Backup ;
- Notifications ;
- Approval Workflow ;
- Web UI ;
- SDK support ;
- Cloud provider integrations ;
- TPM or HSM integrations.

A new module is acceptable only if:

- it has a clear responsibility ;
- it does not duplicate an existing module ;
- it respects Clean Architecture ;
- it avoids circular dependencies ;
- it exposes explicit interfaces ;
- it is testable ;
- it is documented ;
- it does not weaken security invariants.

New modules must be coordinated through the Application Layer.

If a new module changes architecture, security boundaries, public contracts or core domain concepts, the change should be documented in an ADR.

