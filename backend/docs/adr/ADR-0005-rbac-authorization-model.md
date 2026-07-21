# ADR-0005: Adopt Role-Based Access Control (RBAC)

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager requires a strict authorization model.

Authentication answers the question: "Who is making the request?"

Authorization answers a different question: "Is this actor allowed to perform this action on this resource?"

Authentication alone is not sufficient for a Secret Manager.

The project must support:

- multiple users ;
- multiple projects ;
- multiple vaults ;
- service accounts ;
- future AI agents ;
- OpenClaw ;
- least privilege ;
- audit ;
- future evolution.

Secrets are high-impact resources. A single excessive permission can expose credentials, API keys, tokens, private keys or infrastructure access.

The authorization model must prevent:

- excessive access ;
- privilege escalation ;
- duplicated rules ;
- implicit permissions ;
- inconsistent decisions between REST and MCP ;
- difficult audits ;
- hidden access paths ;
- interface-specific security behavior.

OpenClaw must use a dedicated identity with limited permissions.

MCP clients and future AI agents must not gain broad access simply because they interact through MCP.

REST and MCP must receive the same authorization decisions for the same actor, action and resource.

The MVP needs a model that is simple enough to implement and review, but strong enough to express least privilege.

## Decision

MCP Secret Manager adopts Role-Based Access Control (RBAC) for the MVP.

The conceptual model is:

```text
Actor
  -> Role
    -> Permissions
      -> Resources
```

### Actor

An Actor is an identity capable of performing actions.

Examples:

- admin user ;
- service account ;
- OpenClaw ;
- future agent identity.

### Service Account

A Service Account is a non-human actor used by a technical client.

Examples:

- OpenClaw ;
- scripts ;
- applications ;
- MCP servers ;
- future automation.

Service Accounts must receive explicit roles and must not use admin permissions by default.

### Role

A Role groups permissions.

Examples:

- admin ;
- vault_admin ;
- secret_reader ;
- secret_writer ;
- auditor ;
- service_openclaw.

Roles make permission assignment easier to understand and audit.

### Permission

A Permission represents an allowed action.

Examples:

- `vault.read` ;
- `project.read` ;
- `secret.metadata.read` ;
- `secret.value.read` ;
- `secret.create` ;
- `token.revoke` ;
- `audit.read`.

Metadata and value permissions must remain distinct.

### Resource

A Resource is the object affected by an action.

Examples:

- Vault ;
- Project ;
- Secret ;
- SecretVersion ;
- Token ;
- AuditEvent.

### Vault

A Vault is a primary security boundary.

RBAC decisions must be able to reason about access to vault-scoped resources.

### Project

A Project organizes secrets inside a Vault.

RBAC decisions must be able to reason about project-scoped resources.

### Authorization decision location

Authorization decisions are centralized in the Application Layer.

Rules:

- permissions are granted to roles ;
- roles are assigned to actors ;
- application use cases request authorization decisions ;
- REST uses the same decisions ;
- MCP uses the same decisions ;
- no interface owns its own authorization logic ;
- repositories do not make business authorization decisions ;
- crypto is never used to decide authorization.

The absence of a matching permission means denial.

## Alternatives considered

### ACL (Access Control Lists)

Advantages:

- direct resource-level control ;
- easy to reason about for small numbers of resources ;
- flexible per-resource grants ;
- familiar model.

Disadvantages:

- can become difficult to manage at scale ;
- permissions spread across many resources ;
- harder to audit globally ;
- risk of stale grants ;
- more complex administration ;
- less convenient for service accounts and repeated patterns.

Reason rejected:

ACLs are too granular and operationally heavy for the MVP. MCP Secret Manager needs a simpler model that supports reusable permissions and consistent service identities.

### ABAC (Attribute-Based Access Control)

Advantages:

- very expressive ;
- supports context-aware decisions ;
- useful for agents, missions, time, source, environment and risk ;
- strong future fit for AI-first workflows.

Disadvantages:

- significantly more complex ;
- harder to test ;
- harder to audit ;
- requires policy language or evaluator ;
- more risk of implicit behavior ;
- slower MVP.

Reason deferred:

ABAC is valuable for future versions, especially for agent identities and mission context. It is intentionally excluded from the MVP to keep the authorization model simple, explicit and testable.

### Hard-coded permissions

Advantages:

- very simple initially ;
- fast to implement ;
- fewer database concepts ;
- easy for prototypes.

Disadvantages:

- inflexible ;
- difficult to audit ;
- hard to delegate ;
- hard to support service accounts ;
- encourages hidden behavior ;
- requires code changes for access changes ;
- does not scale to OpenClaw, MCP and future agents.

Reason rejected:

Hard-coded permissions are not acceptable for a Secret Manager that must support multiple actors, roles, interfaces and future integrations.

### Authentication only

Advantages:

- simplest possible model ;
- easy to implement ;
- fewer concepts ;
- low initial overhead.

Disadvantages:

- every authenticated actor effectively has broad access ;
- no least privilege ;
- no meaningful service account isolation ;
- no safe OpenClaw role ;
- no safe agent model ;
- poor audit meaning ;
- high blast radius.

Reason rejected:

Authentication-only access is unacceptable. A Secret Manager must distinguish identity from authorization.

### Hybrid model from the MVP

Advantages:

- more expressive from the start ;
- can combine RBAC, ABAC, ACLs and contextual policies ;
- future-ready for agents ;
- powerful for complex environments.

Disadvantages:

- too complex for MVP ;
- larger test matrix ;
- harder documentation ;
- more implementation risk ;
- more chance of conflicting rules ;
- slower delivery ;
- harder review.

Reason rejected:

A hybrid model may be appropriate later, but introducing it in the MVP would violate Simple Before Complex. RBAC provides the right foundation.

## Consequences

### Positive consequences

RBAC provides:

- least privilege ;
- reusable permissions ;
- consistent authorization ;
- easier audit ;
- future evolution path ;
- simpler maintenance ;
- coherent OpenClaw and MCP behavior ;
- clear permission documentation ;
- straightforward tests ;
- reduced duplication.

### Negative consequences

RBAC also introduces:

- more domain concepts ;
- role administration ;
- permission management ;
- documentation overhead ;
- need for careful default roles ;
- tests for role/permission combinations.

These costs are accepted.

## Trade-offs

RBAC is the best compromise for the MVP.

It is more structured than authentication-only or hard-coded permissions, but much simpler than ABAC or a hybrid policy engine.

RBAC is simple enough to:

- document clearly ;
- test thoroughly ;
- implement safely ;
- reason about during reviews ;
- use for OpenClaw ;
- expose consistently through REST and MCP.

It is also extensible enough to support future evolution.

A future hybrid model, such as RBAC plus ABAC, can be introduced later without invalidating the RBAC foundation.

In that future model, RBAC can continue to provide coarse-grained roles while ABAC adds contextual conditions for agents, missions, quotas or environments.

The MVP should establish clear authorization boundaries before adding contextual complexity.

## Related Documents

- `backend/docs/SECURITY.md`
- `backend/docs/DATABASE.md`
- `backend/docs/API_SPEC.md`
- `backend/docs/MCP_SPEC.md`
- `backend/docs/TESTING.md`
- `backend/docs/adr/ADR-0001-clean-architecture.md`
- `backend/docs/adr/ADR-0002-postgresql-primary-storage.md`
- `backend/docs/adr/ADR-0003-envelope-encryption.md`
- `backend/docs/adr/ADR-0004-rest-mcp-dual-interface.md`

## Future evolution

The authorization model may evolve toward:

- hierarchical permissions ;
- dynamic roles ;
- contextual policies ;
- complementary ABAC ;
- organizations ;
- advanced multi-tenant support ;
- agent-specific permissions ;
- mission-scoped access ;
- quotas and budgets.

These evolutions must:

- preserve domain invariants ;
- keep one centralized authorization decision ;
- remain compatible with REST and MCP ;
- preserve audit guarantees ;
- respect least privilege ;
- avoid implicit permissions ;
- remain testable.

Any major change to the authorization model must be documented in a new ADR and reflected in the relevant security, database, API, MCP and testing documentation.

