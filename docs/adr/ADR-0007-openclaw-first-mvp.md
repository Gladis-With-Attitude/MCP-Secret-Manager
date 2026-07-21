# ADR-0007: OpenClaw as the Primary MVP Consumer

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager is designed to be generic enough to serve multiple future consumers.

Expected consumers include:

- OpenClaw ;
- MCP clients ;
- AI agents ;
- applications ;
- scripts ;
- CLI ;
- future SDKs ;
- future Web UI ;
- future agent orchestrators.

However, an MVP needs a primary consumer.

Without a primary consumer, the project risks becoming abstract, over-engineered and difficult to validate.

The MVP has several constraints:

- limit scope ;
- avoid over-engineering ;
- validate the architecture quickly ;
- test real workflows ;
- prepare future clients ;
- keep security guarantees clear ;
- prove REST and MCP behavior ;
- validate RBAC with an actual service identity.

OpenClaw is chosen as the first official consumer because it represents the original and most concrete use case for the project.

OpenClaw provides:

- a real use case ;
- an AI-first integration context ;
- validation of REST API behavior ;
- validation of MCP server behavior ;
- validation of the RBAC model ;
- validation of service account flows ;
- validation of audit events ;
- validation of secret lifecycle workflows.

OpenClaw is close enough to the project's core vision to guide the MVP, while still being specific enough to prevent vague, speculative development.

## Decision

The MVP will be developed primarily for OpenClaw.

OpenClaw is the primary MVP consumer.

This does not mean MCP Secret Manager becomes OpenClaw-specific.

Rules:

- the architecture remains generic ;
- no domain component depends on OpenClaw ;
- OpenClaw is a client, never an internal dependency ;
- REST remains a public interface ;
- MCP remains a public interface ;
- API contracts remain independent from OpenClaw ;
- MCP tools remain independent from OpenClaw ;
- RBAC remains generic ;
- Secret Providers remain generic ;
- the Domain Layer does not know OpenClaw.

### Role of OpenClaw

OpenClaw has three roles in the MVP:

1. Consumer

OpenClaw consumes MCP Secret Manager through public interfaces.

It must authenticate as a service account and use explicit permissions.

2. MVP validator

OpenClaw validates that the MVP supports a real AI infrastructure workflow:

- create vault ;
- create project ;
- store secret ;
- read secret ;
- audit access ;
- restrict permissions.

3. Functional reference

OpenClaw provides the first reference scenario for testing and documentation.

It helps determine MVP priorities, but it does not define private behavior or hidden contracts.

## Alternatives considered

### No official client

Advantages:

- maximum theoretical generality ;
- no bias toward one consumer ;
- simpler to claim broad applicability ;
- avoids integration-specific decisions.

Disadvantages:

- unclear MVP scope ;
- higher risk of over-engineering ;
- harder to validate real workflows ;
- more abstract design debates ;
- no concrete integration pressure ;
- delayed feedback.

Reason rejected:

A Secret Manager without a primary MVP consumer risks solving imaginary problems. OpenClaw provides a real validation target.

### Multiple clients from the MVP

Advantages:

- broader validation ;
- early detection of genericity issues ;
- stronger confidence in public contracts ;
- more representative usage.

Disadvantages:

- larger MVP ;
- more integration work ;
- more documentation ;
- more test matrix ;
- slower delivery ;
- greater risk of premature generalization.

Reason rejected:

The MVP must remain small. Multiple first-class clients can come later after the architecture is validated with OpenClaw.

### Web UI-oriented development

Advantages:

- easier human interaction ;
- more visible product experience ;
- useful for administration ;
- attractive for demos.

Disadvantages:

- UI is not the primary need ;
- adds frontend complexity ;
- can distract from security, API and MCP foundations ;
- does not validate agentic workflows as directly ;
- risks prioritizing convenience over core infrastructure.

Reason rejected:

The MVP should validate the Secret Manager core, REST, MCP, RBAC, audit and OpenClaw integration before building a Web UI.

### API-only development

Advantages:

- clean backend focus ;
- useful for scripts and SDKs ;
- easier to test than full integrations ;
- avoids client-specific complexity.

Disadvantages:

- risks designing unused endpoints ;
- does not fully validate an end-to-end consumer ;
- may miss OpenClaw-specific operational needs ;
- may under-test MCP behavior ;
- weaker AI-first validation.

Reason rejected:

The REST API is essential, but API-only development is not enough. The MVP must be validated through a real consumer and MCP-aware workflow.

### Enterprise-oriented development

Advantages:

- broader feature ambition ;
- support for organizations, teams and policies ;
- closer to large-scale Secret Manager products ;
- future commercial-style readiness.

Disadvantages:

- too broad for MVP ;
- encourages multi-tenant complexity ;
- encourages advanced policy systems too early ;
- delays OpenClaw integration ;
- increases security and testing burden ;
- conflicts with Simple Before Complex.

Reason rejected:

MCP Secret Manager starts as a self-hosted AI-first Secret Manager. Enterprise features can be added later when justified by real needs.

## Consequences

### Positive consequences

This decision provides:

- focused MVP ;
- faster validation ;
- less complexity ;
- better priorities ;
- architecture validated on a real use case ;
- AI-native integration ;
- concrete RBAC validation ;
- concrete audit validation ;
- concrete REST/MCP validation ;
- clearer documentation and tests.

### Negative consequences

This decision also has risks:

- some needs of other clients are deferred ;
- potential bias toward OpenClaw workflows ;
- need to actively preserve genericity ;
- future clients may reveal missing abstractions ;
- documentation must distinguish OpenClaw examples from core requirements.

These risks are accepted and mitigated by keeping public contracts independent.

## Trade-offs

Choosing a primary MVP consumer reduces risk.

It gives the project a real workflow to satisfy and prevents speculative feature design.

The trade-off is that OpenClaw may influence early priorities. This is acceptable as long as OpenClaw does not become an internal dependency or private architectural assumption.

To prevent OpenClaw-specific architecture:

- OpenClaw uses public REST and MCP contracts ;
- OpenClaw is represented as a Service Account ;
- OpenClaw permissions use the generic RBAC model ;
- OpenClaw secrets live in normal Vaults, Projects, Secrets and SecretVersions ;
- no Domain concept is named after or coupled to OpenClaw ;
- tests may include OpenClaw scenarios but must validate generic behavior.

Public contracts remain independent of the consumer.

REST and MCP must remain suitable for future clients.

## Related Documents

- `docs/PROJECT.md`
- `docs/API_SPEC.md`
- `docs/MCP_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/SECURITY.md`
- `docs/adr/ADR-0001-clean-architecture.md`
- `docs/adr/ADR-0002-postgresql-primary-storage.md`
- `docs/adr/ADR-0003-envelope-encryption.md`
- `docs/adr/ADR-0004-rest-mcp-dual-interface.md`
- `docs/adr/ADR-0005-rbac-authorization-model.md`
- `docs/adr/ADR-0006-documentation-first-development.md`

## Future evolution

Future consumers may include:

- CLI ;
- SDK Python ;
- SDK TypeScript ;
- applications ;
- Web UI ;
- agent orchestrators ;
- other projects ;
- additional MCP servers ;
- automation systems.

Adding new consumers must never:

- modify core business rules for one client ;
- modify the Domain Layer for a specific client ;
- create an internal dependency on a client ;
- bypass RBAC ;
- bypass audit ;
- undermine REST or MCP as public interfaces ;
- create private behavior unavailable through documented contracts.

New consumers should be added as clients or adapters around the same Application Layer use cases.

Any future change that makes a specific consumer influence the Domain or security model must be documented in a new ADR.

