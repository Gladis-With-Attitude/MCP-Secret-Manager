# ADR-0001: Adopt Clean Architecture

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager is a security-critical project.

It is not a simple web application and must not be structured as one. It is a Secret Manager designed to protect sensitive values used by OpenClaw, MCP servers, AI agents, applications, scripts and future orchestrators.

The project has several important constraints:

- it stores and protects secrets ;
- it is AI-first ;
- OpenClaw is the first official consumer ;
- it exposes a REST API ;
- it exposes an MCP server ;
- it must enforce strict security boundaries ;
- it must remain testable ;
- it must support future extension ;
- it must preserve separation of responsibilities ;
- it must avoid duplicating security logic across interfaces.

The same business operation may be triggered through REST, MCP, CLI or future SDKs.

For example, reading a secret value must always follow the same rules:

- authenticate the actor ;
- resolve the resource ;
- verify permissions ;
- verify vault state ;
- decrypt only after authorization ;
- audit the access ;
- return a minimal response.

This workflow must not be reimplemented separately in REST handlers, MCP tools or CLI commands.

A classic MVC architecture or framework-centric design would make the framework the center of the system. That would be dangerous for this project because security rules could become spread across controllers, routers, models, middleware and database code.

MCP Secret Manager needs the opposite: the domain and application rules must be the center, and frameworks must remain adapters.

## Decision

MCP Secret Manager adopts Clean Architecture.

The project is organized conceptually into four layers:

```text
Presentation
  -> Application
    -> Domain
      -> Infrastructure
```

Dependencies point inward.

Outer layers may depend on inner layers. Inner layers must not depend on outer layers.

### Presentation Layer

The Presentation Layer exposes the system to clients.

It contains:

- REST API ;
- MCP server ;
- CLI ;
- future external adapters.

Responsibilities:

- receive external requests ;
- validate external input format ;
- extract authentication material ;
- translate requests into application use cases ;
- translate application responses into protocol responses ;
- translate application errors into protocol errors.

The Presentation Layer must not contain core business rules, authorization decisions, cryptographic workflows or database logic.

REST and MCP are both Presentation Layer adapters.

MCP is not a wrapper around REST. REST and MCP must both call the Application Layer directly.

### Application Layer

The Application Layer orchestrates use cases.

Responsibilities:

- execute business workflows ;
- enforce the order of security operations ;
- request permission checks ;
- coordinate secret lifecycle operations ;
- invoke crypto only after authorization ;
- invoke audit for sensitive actions ;
- coordinate repositories through abstractions.

This layer contains the application behavior that must be shared by REST, MCP, CLI and future SDKs.

### Domain Layer

The Domain Layer contains the core concepts and invariants of MCP Secret Manager.

It contains concepts such as:

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- SecretProvider ;
- Actor ;
- Role ;
- Permission ;
- AuditEvent.

Responsibilities:

- define valid states ;
- protect domain invariants ;
- model core business concepts ;
- remain independent of frameworks, protocols and databases.

The Domain Layer must not depend on FastAPI, MCP, PostgreSQL, Docker, SQLAlchemy or any external protocol.

### Infrastructure Layer

The Infrastructure Layer implements technical details.

It contains:

- PostgreSQL repositories ;
- migrations ;
- cryptographic implementation ;
- token persistence ;
- configuration loading ;
- health checks ;
- external provider adapters.

Responsibilities:

- persist data ;
- implement repository contracts ;
- provide concrete crypto operations ;
- connect to external systems ;
- implement technical details required by the Application Layer.

Infrastructure provides capabilities. It does not own the business policy.

### Dependency Inversion

The project applies Dependency Inversion.

The Application Layer depends on contracts and abstractions, not concrete infrastructure details.

Concrete infrastructure implementations depend on those contracts.

This allows:

- testing use cases without PostgreSQL ;
- testing permission logic without REST or MCP ;
- replacing adapters without changing domain rules ;
- keeping security workflows centralized ;
- avoiding framework lock-in.

## Alternatives considered

### MVC

Advantages:

- familiar to many developers ;
- simple for small web applications ;
- quick to start with common frameworks.

Disadvantages:

- tends to couple business logic to controllers and models ;
- can spread authorization logic across endpoints ;
- does not naturally support multiple first-class interfaces like REST and MCP ;
- encourages framework-centric organization ;
- makes security boundaries less explicit.

Reason rejected:

MCP Secret Manager is not a classic web application. MVC does not provide strong enough boundaries for a security-critical, multi-interface Secret Manager.

### Classic Layered Architecture

Advantages:

- simple mental model ;
- common in backend applications ;
- separates presentation, service and data access to some extent.

Disadvantages:

- dependencies often flow downward toward the database ;
- domain logic can become dependent on persistence models ;
- services can become tightly coupled to repositories ;
- frameworks and database choices can leak into business logic.

Reason rejected:

Classic layered architecture improves organization but does not enforce the inward dependency rule strongly enough for this project.

### Hexagonal Architecture

Advantages:

- strong separation between core and adapters ;
- good fit for multiple interfaces ;
- testable ;
- compatible with ports and adapters.

Disadvantages:

- terminology can be less immediately clear to contributors ;
- can become abstract if introduced too early ;
- overlaps significantly with Clean Architecture for this project's needs.

Reason not chosen as primary framing:

Hexagonal Architecture is compatible with the intended design, but Clean Architecture provides clearer layer language for this project: Presentation, Application, Domain and Infrastructure.

The project may still use ports-and-adapters ideas where useful.

### Framework-centric design

Advantages:

- very fast initial development ;
- follows framework conventions ;
- fewer files at the beginning ;
- easy for simple CRUD applications.

Disadvantages:

- framework becomes the architecture ;
- business rules often live in handlers, models or middleware ;
- difficult to keep REST and MCP consistent ;
- harder to test use cases without framework runtime ;
- higher risk of security bypasses ;
- harder to evolve toward new interfaces.

Reason rejected:

The project must outlive its initial framework choices. FastAPI is an implementation detail of the MVP, not the center of the system.

### Monolith without separation

Advantages:

- fastest initial implementation ;
- minimal ceremony ;
- fewer abstractions.

Disadvantages:

- security logic becomes scattered ;
- tests become harder ;
- changes become risky ;
- REST, MCP and CLI can diverge ;
- audit and permissions can be bypassed accidentally ;
- future evolution becomes expensive.

Reason rejected:

A Secret Manager cannot rely on informal discipline alone. The project needs explicit boundaries from the beginning.

## Consequences

### Positive consequences

Adopting Clean Architecture provides:

- better testability ;
- clearer security boundaries ;
- shared behavior across REST, MCP and CLI ;
- less duplication of permission logic ;
- better separation between domain and framework ;
- easier documentation ;
- improved maintainability ;
- safer future evolution ;
- clearer OpenClaw integration ;
- easier addition of future clients and providers ;
- stronger review criteria.

### Negative consequences

This decision also has costs:

- more files ;
- more concepts to learn ;
- more discipline required ;
- higher initial implementation cost ;
- more explicit wiring ;
- more review attention needed to preserve boundaries.

These costs are real and accepted.

## Trade-offs

Clean Architecture introduces more structure than a framework-centric MVP.

For a simple CRUD application, that cost might be unnecessary. MCP Secret Manager is not a simple CRUD application.

The project handles secrets, permissions, cryptography, audit, REST, MCP and future agentic workflows. A small amount of architectural structure early prevents dangerous duplication and coupling later.

The additional cost is acceptable because it directly supports:

- security ;
- testability ;
- auditability ;
- multi-interface consistency ;
- long-term maintainability ;
- future OpenClaw and agent integrations.

The architecture must still remain pragmatic. Clean Architecture should not become an excuse for unnecessary abstractions.

## Related Documents

- `docs/ARCHITECTURE.md`
- `docs/API_SPEC.md`
- `docs/MCP_SPEC.md`
- `docs/TESTING.md`
- `docs/CONSTITUTION.md`

## Future evolution

This decision may evolve only if a future architecture provides stronger guarantees without compromising:

- security ;
- testability ;
- documentation ;
- separation of responsibilities ;
- REST/MCP consistency ;
- auditability ;
- maintainability.

Any future change to this decision must be documented in a new ADR.

