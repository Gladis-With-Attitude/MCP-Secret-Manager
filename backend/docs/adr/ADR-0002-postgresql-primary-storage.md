# ADR-0002: PostgreSQL as Primary Storage

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager needs robust persistent storage.

The project stores and coordinates critical state for a security-sensitive system:

- vault metadata ;
- project metadata ;
- secret metadata ;
- encrypted secret versions ;
- actors ;
- service accounts ;
- roles ;
- permissions ;
- tokens ;
- audit events ;
- persistent configuration state.

MCP Secret Manager never stores secret values in plaintext.

Secret values are encrypted by the application before persistence. PostgreSQL stores ciphertexts, cryptographic metadata, domain metadata, audit records and authorization data. The database is a persistence layer, not a cryptographic trust boundary by itself.

The project has several storage constraints:

- secure storage of metadata ;
- storage of secret versions ;
- immutable audit history ;
- roles and permissions ;
- token metadata and revocation state ;
- transactions ;
- data consistency ;
- reasonable scalability ;
- MVP simplicity ;
- reliable migrations ;
- historical data preservation.

The domain is highly relational.

Examples:

- a Project belongs to one Vault ;
- a Secret belongs to one Project ;
- a SecretVersion belongs to one Secret ;
- an Actor can have many Roles ;
- a Role can have many Permissions ;
- a Token belongs to one Actor ;
- an AuditEvent references an Actor, an action and a resource.

These relationships benefit from a relational database.

The project needs:

- referential integrity ;
- ACID transactions ;
- constraints ;
- indexes ;
- reliable queries ;
- migrations ;
- historical records ;
- predictable behavior under concurrent access.

Because MCP Secret Manager is a Secret Manager, storage correctness is a security property. Losing track of a token revocation, permission assignment, secret version or audit event can become a security issue.

## Decision

MCP Secret Manager adopts PostgreSQL as the official primary storage engine.

PostgreSQL is responsible for persisting:

- Vaults ;
- Projects ;
- Secrets ;
- SecretVersions ;
- Actors ;
- ServiceAccounts ;
- Roles ;
- Permissions ;
- RolePermissions ;
- ActorRoles ;
- Tokens ;
- AuditEvents ;
- persistent configuration state when needed.

PostgreSQL is responsible only for persistence.

It must not own business decisions.

Business workflows remain in the Application Layer.

Domain invariants remain in the Domain Layer.

Authorization decisions remain in the permission-related application services.

Cryptographic decisions remain in the crypto design and crypto services.

Audit semantics remain in the application and audit modules.

Repositories are abstractions used by the Application Layer.

PostgreSQL repositories are the MVP implementation of those repository abstractions.

This preserves Clean Architecture:

```text
Application Layer
  -> Repository Contracts
    <- PostgreSQL Repository Implementations
```

The Application Layer expresses what it needs to load or persist. PostgreSQL implements how that data is stored.

## Alternatives considered

### SQLite

Advantages:

- very simple local setup ;
- no separate database server ;
- easy for small prototypes ;
- low operational overhead ;
- good for embedded development.

Disadvantages:

- weaker fit for concurrent service workloads ;
- less suitable for long-running server deployment ;
- less operationally aligned with Dockerized infrastructure ;
- more limited for production-style access patterns ;
- not ideal for audit-heavy, multi-client usage ;
- would encourage a different MVP than the intended Debian/OpenClaw deployment.

Reason rejected as primary storage:

SQLite is useful for prototypes and local tools, but MCP Secret Manager is designed as a server component for OpenClaw, MCP servers and services. PostgreSQL better matches the persistence, concurrency, audit and operational requirements.

SQLite is not part of the MVP storage strategy.

### MySQL

Advantages:

- mature relational database ;
- widely deployed ;
- good ecosystem ;
- supports transactions ;
- familiar to many operators.

Disadvantages:

- PostgreSQL has stronger alignment with advanced relational modeling ;
- PostgreSQL has excellent support for constraints, indexing and JSONB metadata ;
- PostgreSQL is often preferred for correctness-heavy application data ;
- using MySQL would not provide a meaningful MVP advantage.

Reason PostgreSQL is preferred:

PostgreSQL provides the best combination of relational rigor, extensibility, JSONB support, migrations ecosystem, operational maturity and developer familiarity for this project.

### MongoDB

Advantages:

- flexible document model ;
- easy to store heterogeneous metadata ;
- convenient for rapidly changing shapes ;
- scalable for some document-oriented workloads.

Disadvantages:

- weaker fit for strongly relational data ;
- relationships and constraints would move into application code ;
- harder to enforce integrity between vaults, projects, secrets, versions, roles and permissions ;
- audit and authorization data benefit from relational consistency ;
- flexible schemas increase the risk of ambiguous states.

Reason rejected:

MCP Secret Manager needs strict relationships, constraints and transactionally consistent state. MongoDB's flexibility is less valuable than PostgreSQL's integrity guarantees for this domain.

### JSON/YAML files

Advantages:

- very simple ;
- human-readable ;
- easy to inspect ;
- no database service ;
- useful for examples or static configuration.

Disadvantages:

- poor concurrency ;
- weak integrity guarantees ;
- difficult audit history ;
- difficult transactions ;
- risky for tokens and permissions ;
- hard to manage migrations safely ;
- unsuitable for growing secret version history ;
- high risk of accidental plaintext leakage.

Reason rejected:

JSON or YAML files are not appropriate as primary storage for a Secret Manager. They may be useful for configuration or import/export formats, but not for authoritative persistence.

### In-memory storage only

Advantages:

- simple ;
- fast ;
- useful for tests ;
- no external dependency ;
- easy to reset.

Disadvantages:

- no persistence ;
- no recovery ;
- no durable audit ;
- no token revocation history after restart ;
- no reliable secret version history ;
- impossible to operate as infrastructure.

Reason rejected:

MCP Secret Manager requires durable state. In-memory storage may be useful for tests, but cannot be a primary storage engine.

### Multi-database from the MVP

Advantages:

- theoretical portability ;
- easier adoption by users with different database preferences ;
- stronger abstraction pressure ;
- potential future flexibility.

Disadvantages:

- significant implementation cost ;
- migration complexity ;
- lowest-common-denominator schema design ;
- harder testing matrix ;
- more security review burden ;
- more documentation ;
- slower MVP ;
- greater risk of inconsistent behavior.

Reason rejected:

The MVP should be simple, robust and secure. Supporting multiple databases before a real need exists would add complexity without improving the core guarantees.

Repository abstractions are sufficient to preserve future optionality.

## Consequences

### Positive consequences

Using PostgreSQL provides:

- robust transactions ;
- strong referential integrity ;
- constraints ;
- reliable migrations ;
- durable audit records ;
- support for complex queries ;
- mature indexing ;
- stability ;
- operational maturity ;
- rich ecosystem ;
- good backup tooling ;
- good Docker support ;
- clear fit for relational permissions and secret lifecycle data.

### Negative consequences

This decision also has costs:

- PostgreSQL becomes a required dependency ;
- operation is more complex than a local file ;
- migrations must be maintained ;
- deployment has more moving parts than SQLite ;
- a database must be available for the service to operate ;
- local development requires PostgreSQL or a compatible dev environment.

These costs are accepted.

## Trade-offs

PostgreSQL is the best compromise for MCP Secret Manager's MVP.

It balances:

- simplicity ;
- robustness ;
- security ;
- maintainability ;
- performance ;
- evolvability.

It is simple enough to run locally with Docker and mature enough for long-term self-hosted production.

It supports the domain model naturally:

- vault hierarchy ;
- projects ;
- secrets ;
- immutable versions ;
- RBAC ;
- tokens ;
- audit events.

It is unnecessary to support multiple database engines in the MVP.

Multi-database support would increase the testing matrix, migration burden and risk of behavioral divergence. For a security project, consistency is more valuable than theoretical portability.

The Repository abstraction preserves future flexibility without forcing premature generalization.

If another storage engine becomes justified later, it can be introduced as a new repository implementation while preserving the Domain and Application Layers.

## Related Documents

- `backend/docs/ARCHITECTURE.md`
- `backend/docs/DATABASE.md`
- `backend/docs/SECURITY.md`
- `backend/docs/TESTING.md`
- `backend/docs/CONSTITUTION.md`
- `backend/docs/adr/ADR-0001-clean-architecture.md`

## Future evolution

The project may eventually support other persistence engines.

Such an evolution is acceptable only if it:

- preserves domain invariants ;
- respects Clean Architecture ;
- does not modify the Domain Layer ;
- does not modify the Application Layer for storage-specific reasons ;
- preserves security guarantees ;
- preserves audit guarantees ;
- remains compatible with migration strategy ;
- does not create inconsistent behavior between storage backends.

PostgreSQL remains the official reference storage engine until a real, documented need justifies another implementation.

Any future decision to support another primary storage engine must be documented in a new ADR.

