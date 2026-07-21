# ADR-0006: Documentation-First Development

## Status

Accepted

## Date

YYYY-MM-DD

## Context

AI-driven projects and security projects can drift quickly when code becomes the only source of truth.

MCP Secret Manager is both:

- an AI-first project ;
- a security-critical project.

This creates specific constraints:

- AI-assisted development ;
- multiple future human contributors ;
- durable documentation ;
- stable architecture ;
- security-sensitive decisions ;
- easier reviews ;
- contributor onboarding ;
- future evolution ;
- traceable design decisions.

When development is code-first, important decisions often become implicit.

The risks include:

- implicit architecture ;
- lost decisions ;
- outdated documentation ;
- undocumented behavior ;
- difficult reviews ;
- security drift ;
- inconsistent AI-generated contributions ;
- unclear boundaries ;
- hidden assumptions ;
- repeated debates ;
- divergence between REST, MCP and internal use cases.

For a Secret Manager, this is dangerous.

The project must be able to explain why it behaves the way it does.

Future contributors, maintainers and AI assistants must be able to read the project's source of truth before changing behavior.

Documentation is not secondary to the code. It is part of the security model and governance model of the project.

## Decision

MCP Secret Manager adopts Documentation-First Development.

The official workflow is:

```text
Idea
  -> Discussion
    -> Documentation
      -> ADR if needed
        -> Validation
          -> Implementation
            -> Tests
              -> Documentation Update
```

Rules:

- documentation is the source of truth ;
- ADRs document structural decisions ;
- code implements documented behavior ;
- major architectural changes start with documentation ;
- security-sensitive changes require documentation alignment ;
- AI assistants must respect the documentation hierarchy ;
- undocumented behavior must not become an implicit contract ;
- documentation and code must remain aligned.

### Role of PROJECT.md

`backend/docs/PROJECT.md` defines the project vision, philosophy, goals, MVP scope and long-term direction.

It explains what MCP Secret Manager is and what it is not.

### Role of CONSTITUTION.md

`backend/docs/CONSTITUTION.md` defines the principles that Pull Requests must not violate.

It is the highest-level governance document.

### Role of ARCHITECTURE.md

`backend/docs/ARCHITECTURE.md` defines the internal architecture, layers, dependencies, modules, flows and invariants.

It guides where features should be added.

### Role of SECURITY.md

`backend/docs/SECURITY.md` defines the official security strategy, threat model, security model, incident approach and production expectations.

It guides all security-sensitive changes.

### Role of DATABASE.md

`backend/docs/DATABASE.md` defines the domain data model, entities, relationships, lifecycles and invariants.

It guides database design before migrations or ORM models exist.

### Role of CRYPTOGRAPHY.md

`backend/docs/CRYPTOGRAPHY.md` defines the cryptographic strategy, key hierarchy, lifecycle and invariants.

It guides all cryptographic implementation decisions.

### Role of API_SPEC.md

`backend/docs/API_SPEC.md` defines the REST API functional contract.

It guides endpoints, resources, errors, permissions and REST invariants.

### Role of MCP_SPEC.md

`backend/docs/MCP_SPEC.md` defines the MCP interface contract.

It guides tools, permissions, responses, audit and agent-specific security.

### Role of TESTING.md

`backend/docs/TESTING.md` defines the official testing and quality strategy.

It guides what must be tested before merge.

### Role of AI_RULES.md

`backend/docs/AI_RULES.md` defines how AI assistants are allowed to contribute.

It guides AI-assisted analysis, implementation, review and documentation.

### Role of CONTRIBUTING.md

`backend/docs/CONTRIBUTING.md` defines the contribution process for humans and assisted workflows.

It guides issues, branches, Pull Requests, review and merge expectations.

### Role of ADRs

ADRs document structural decisions.

They explain:

- context ;
- decision ;
- alternatives ;
- consequences ;
- trade-offs ;
- related documents ;
- future evolution.

An ADR is required or strongly recommended for decisions that affect architecture, security, storage, cryptography, authorization, public interfaces or governance.

## Alternatives considered

### Code First

Advantages:

- faster initial development ;
- less upfront writing ;
- rapid prototyping ;
- immediate feedback from implementation.

Disadvantages:

- decisions become implicit ;
- architecture can drift ;
- documentation lags behind ;
- AI-generated changes become harder to constrain ;
- security assumptions may be hidden ;
- reviews require reconstructing intent from code ;
- future contributors lose context.

Reason rejected:

Code First is too risky for a security-critical, AI-assisted project. MCP Secret Manager needs explicit decisions before implementation.

### Documentation after implementation

Advantages:

- implementation can reveal practical constraints ;
- less chance of documenting impossible designs ;
- useful for small changes ;
- lower initial process cost.

Disadvantages:

- documentation is often skipped ;
- docs become a description of accidents ;
- reviewers lack a prior contract ;
- AI assistants may follow code patterns that should not exist ;
- security decisions may never be written down.

Reason rejected:

Documentation after implementation is not strong enough as the default process. It may be acceptable for small corrections, but structural behavior must be documented before or with implementation.

### Minimal documentation

Advantages:

- less maintenance burden ;
- faster contribution flow ;
- lower writing cost ;
- easier for small projects.

Disadvantages:

- insufficient for security governance ;
- weak onboarding ;
- repeated architectural debates ;
- unclear invariants ;
- difficult AI alignment ;
- higher review burden ;
- greater risk of inconsistent behavior.

Reason rejected:

MCP Secret Manager needs more than minimal documentation because it has security, AI, MCP, REST, database, crypto and contribution governance requirements.

### Unversioned wiki

Advantages:

- easy to edit ;
- convenient for discussion ;
- accessible to non-developers ;
- useful for informal notes.

Disadvantages:

- not reviewed with code ;
- history may be disconnected from implementation ;
- can diverge from repository state ;
- not naturally tied to Pull Requests ;
- harder for local tooling and AI agents to consume reliably.

Reason rejected:

Documentation that governs implementation must live in the repository and be versioned with the project.

An external wiki may supplement the project later, but it must not become the source of truth.

### Implicit architecture

Advantages:

- no process overhead ;
- contributors can move quickly ;
- architecture emerges organically ;
- fewer documents.

Disadvantages:

- boundaries are unclear ;
- framework choices dominate ;
- security logic can spread ;
- REST and MCP can diverge ;
- tests become less targeted ;
- AI assistants infer inconsistent patterns ;
- maintainability degrades over time.

Reason rejected:

Implicit architecture is unacceptable for MCP Secret Manager. The project requires explicit boundaries and documented invariants.

## Consequences

### Positive consequences

Documentation-First Development provides:

- better coherence ;
- easier onboarding ;
- traceable decisions ;
- better reviews ;
- more reliable AI assistance ;
- stable architecture ;
- easier maintenance ;
- clearer security posture ;
- fewer repeated debates ;
- stronger alignment between humans and AI tools.

### Negative consequences

This decision also has costs:

- more upfront time ;
- documentation must be maintained ;
- discipline is required ;
- risk of over-documentation ;
- some changes may feel slower ;
- contributors must read more context.

These costs are accepted.

## Trade-offs

Investing in documentation is profitable for a long-term security project.

The cost of documenting decisions early is lower than the cost of rediscovering them after a security regression, architecture drift or inconsistent AI-generated contribution.

Documentation also reduces AI errors.

AI assistants perform better when they have explicit constraints, stable vocabulary, clear invariants and documented workflows. Without these, they may generate plausible but incorrect code.

Documentation must remain pragmatic.

It should guide decisions, clarify behavior and preserve security guarantees. It must not become an end in itself. Documentation that does not improve understanding, safety, onboarding or maintainability should be avoided.

The goal is not to write more documents.

The goal is to keep the project understandable and safe.

## Related Documents

- `backend/docs/PROJECT.md`
- `backend/docs/CONSTITUTION.md`
- `backend/docs/ARCHITECTURE.md`
- `backend/docs/SECURITY.md`
- `backend/docs/TESTING.md`
- `backend/docs/AI_RULES.md`
- `backend/docs/CONTRIBUTING.md`
- `backend/docs/adr/ADR-0001-clean-architecture.md`
- `backend/docs/adr/ADR-0002-postgresql-primary-storage.md`
- `backend/docs/adr/ADR-0003-envelope-encryption.md`
- `backend/docs/adr/ADR-0004-rest-mcp-dual-interface.md`
- `backend/docs/adr/ADR-0005-rbac-authorization-model.md`

## Future evolution

The Documentation-First process may evolve.

Any evolution must:

- preserve a single source of truth ;
- keep decisions traceable ;
- remain compatible with AI-assisted development ;
- maintain security guarantees ;
- preserve review quality ;
- keep documentation versioned ;
- avoid creating hidden governance outside the repository.

Future improvements may include:

- ADR templates ;
- documentation linting ;
- automated documentation checks ;
- docs-to-code consistency checks ;
- AI review prompts ;
- release documentation gates.

Any major change to the documentation governance process must be documented in a new ADR.

