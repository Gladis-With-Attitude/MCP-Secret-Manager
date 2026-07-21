# ADR-0004: REST and MCP as First-Class Interfaces

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager must be used by multiple types of consumers.

Expected consumers include:

- OpenClaw ;
- MCP clients ;
- applications ;
- scripts ;
- future SDKs ;
- a possible future Web interface ;
- future agent orchestrators.

The project exposes different protocols for different use cases.

REST is appropriate for:

- OpenClaw integration ;
- scripts ;
- applications ;
- SDKs ;
- administrative automation ;
- future Web UI backend interactions.

MCP is appropriate for:

- AI agents ;
- MCP clients ;
- agent orchestrators ;
- tool-based workflows ;
- AI-first integrations.

The project has several constraints:

- one business logic ;
- multiple protocols ;
- consistent behavior ;
- identical security guarantees ;
- identical authorization decisions ;
- consistent audit semantics ;
- future extensibility ;
- maintainability.

It would be dangerous to make MCP a simple proxy to REST, or REST a simple proxy to MCP.

The risks include:

- duplicated behavior ;
- divergent authorization ;
- different audit events ;
- inconsistent error handling ;
- protocol-specific workarounds ;
- hidden coupling ;
- harder testing ;
- maintenance errors ;
- unclear source of truth.

MCP Secret Manager needs REST and MCP to be independent adapters over the same application use cases.

The Application Layer must remain the source of business workflows.

No protocol should become the business reference implementation.

## Decision

REST and MCP are first-class interfaces.

Both are Presentation Layer adapters.

They call the same Application Layer use cases directly.

Conceptually:

```text
REST Adapter
     |
     v
Application Layer
     ^
     |
MCP Adapter
```

Rules:

- REST calls application use cases directly ;
- MCP calls the same application use cases directly ;
- REST does not depend on MCP ;
- MCP does not depend on REST ;
- no protocol wraps the other internally ;
- business rules are shared ;
- authorization decisions are unique ;
- audit semantics are consistent ;
- security invariants apply equally to both interfaces.

### REST

REST exposes resource-oriented HTTP operations.

Responsibilities:

- receive HTTP requests ;
- validate HTTP payloads ;
- map requests to application use cases ;
- map application errors to HTTP errors ;
- expose stable public contracts ;
- support OpenClaw, CLI, SDKs and scripts.

REST must not contain core business rules.

REST must not directly access PostgreSQL for business operations.

REST must not directly perform decryption.

### MCP

MCP exposes explicit tools for agents and MCP clients.

Responsibilities:

- expose safe MCP tools ;
- validate tool arguments ;
- map tool calls to application use cases ;
- produce minimal agent-appropriate responses ;
- map application errors to MCP-safe errors ;
- preserve tool-level audit context.

MCP must not contain core business rules.

MCP must not directly access PostgreSQL for business operations.

MCP must not directly perform decryption.

### Application

The Application Layer owns use case orchestration.

Responsibilities:

- apply authorization ;
- enforce operation order ;
- coordinate domain rules ;
- invoke crypto after authorization ;
- invoke audit for sensitive actions ;
- coordinate repositories through abstractions.

This layer ensures REST and MCP behave consistently.

### Domain

The Domain Layer owns core concepts and invariants.

Responsibilities:

- model Vaults, Projects, Secrets, SecretVersions, Actors, Roles, Permissions and AuditEvents ;
- enforce domain invariants ;
- remain independent of REST and MCP.

### Infrastructure

The Infrastructure Layer provides technical implementations.

Responsibilities:

- PostgreSQL persistence ;
- cryptographic implementation ;
- token storage ;
- audit persistence ;
- configuration ;
- external integrations.

Infrastructure supports the Application Layer. It does not define protocol behavior.

## Alternatives considered

### MCP as a REST wrapper

Advantages:

- easier initial implementation ;
- reuse existing REST routes ;
- fewer direct application calls ;
- one external protocol path to test initially.

Disadvantages:

- MCP becomes coupled to HTTP semantics ;
- MCP inherits REST response shapes that may not be appropriate for agents ;
- error handling becomes indirect ;
- audit context may be lost or distorted ;
- performance overhead ;
- harder to express MCP-specific constraints ;
- REST becomes the hidden source of truth.

Reason rejected:

MCP is a first-class interface for AI agents. It must not be reduced to an internal REST client. It needs direct access to application use cases while preserving MCP-specific response and audit semantics.

### REST as a MCP wrapper

Advantages:

- one tool-based internal path ;
- MCP becomes central ;
- possible reuse of MCP tools.

Disadvantages:

- REST becomes coupled to tool semantics ;
- resource-oriented API design becomes awkward ;
- SDK and script clients inherit agent-oriented behavior ;
- HTTP errors and contracts become harder to keep stable ;
- MCP becomes the hidden business reference ;
- inappropriate for OpenClaw and traditional clients.

Reason rejected:

REST has its own valid role for OpenClaw, scripts, applications and SDKs. It must remain a proper REST interface over application use cases.

### Two separate business implementations

Advantages:

- each protocol can be optimized independently ;
- teams could work separately ;
- fewer shared abstractions initially.

Disadvantages:

- duplicated security logic ;
- high risk of authorization divergence ;
- high risk of audit divergence ;
- bugs fixed in one interface may remain in the other ;
- more tests required ;
- harder maintenance ;
- violates Clean Architecture.

Reason rejected:

Duplicating business logic across REST and MCP is unacceptable for a Secret Manager. Authorization, crypto sequencing and audit must be shared.

### REST only

Advantages:

- simpler MVP ;
- widely understood ;
- easy for OpenClaw, scripts and SDKs ;
- fewer interfaces to document and test.

Disadvantages:

- does not satisfy MCP-native vision ;
- less natural for AI agents ;
- would force agents through generic HTTP clients ;
- misses first-class tool semantics ;
- weakens AI-first positioning.

Reason rejected:

MCP Secret Manager is AI-first and MCP-native. REST alone is insufficient for the project's core identity and intended agent workflows.

### MCP only

Advantages:

- strong AI-first focus ;
- simpler agent integration ;
- one interface to maintain initially ;
- avoids REST surface area.

Disadvantages:

- less suitable for scripts and applications ;
- harder SDK and Web UI integration ;
- awkward for traditional automation ;
- less standard for administrative HTTP workflows ;
- not ideal as OpenClaw's only integration path.

Reason rejected:

MCP is essential, but not sufficient alone. MCP Secret Manager must also support traditional service and automation clients through REST.

## Consequences

### Positive consequences

This decision provides:

- one business logic ;
- identical behavior across interfaces ;
- consistent security ;
- consistent audit ;
- simpler shared testing of use cases ;
- easier maintenance ;
- easier addition of new protocols ;
- cleaner OpenClaw integration ;
- proper MCP-native behavior ;
- stable REST contracts.

### Negative consequences

This decision also has costs:

- two adapters to maintain ;
- more integration tests ;
- more documentation ;
- stricter architectural discipline ;
- need to verify REST/MCP consistency ;
- more initial design work.

These costs are accepted.

## Trade-offs

Maintaining two adapters is preferable to duplicating business rules.

The key distinction is that adapters are allowed to differ in protocol shape, but not in business decision.

REST may expose resource-oriented endpoints.

MCP may expose tool-oriented actions.

Both must call the same use cases.

This decision naturally prepares the project for:

- CLI ;
- SDK Python ;
- SDK TypeScript ;
- Web UI ;
- GraphQL ;
- gRPC ;
- future agent protocols.

Each future interface can be added as another adapter without changing the Domain or duplicating authorization logic.

The trade-off is more adapter code, but less duplicated security logic.

For a Secret Manager, this is the correct trade-off.

## Related Documents

- `docs/API_SPEC.md`
- `docs/MCP_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/SECURITY.md`
- `docs/adr/ADR-0001-clean-architecture.md`
- `docs/adr/ADR-0002-postgresql-primary-storage.md`
- `docs/adr/ADR-0003-envelope-encryption.md`

## Future evolution

New adapters may be added in the future.

Examples:

- GraphQL ;
- gRPC ;
- CLI ;
- SDK-specific adapters ;
- Web UI ;
- future agent protocols.

Every new adapter must:

- call the Application Layer directly ;
- respect the same invariants ;
- produce the same security guarantees ;
- produce the same audit guarantees ;
- avoid duplicating business rules ;
- avoid becoming the business reference implementation ;
- remain independent from other protocol adapters.

No adapter should become privileged.

The Application Layer remains the shared source of business workflows.

Any future change to this interface strategy must be documented in a new ADR.

