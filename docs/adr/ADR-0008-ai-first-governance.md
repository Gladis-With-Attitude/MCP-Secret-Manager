# ADR-0008: AI-First Governance

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager is developed with significant AI assistance.

This is intentional.

The project is AI-first both in its product vision and in its development workflow. AI assistants can help with documentation, architecture analysis, implementation, tests, reviews, migration planning and security reasoning.

The project has several constraints:

- generative AI assistance ;
- multiple models over time ;
- multiple human contributors ;
- security-critical behavior ;
- code quality ;
- durable documentation ;
- reproducibility ;
- traceability ;
- maintainability.

AI assistance creates substantial benefits, but it also introduces risks.

Risks include:

- hallucinations ;
- implicit decisions ;
- undocumented code ;
- architecture drift ;
- duplicated logic ;
- technical debt ;
- unreviewed behavior ;
- plausible but incorrect explanations ;
- security assumptions presented as facts ;
- tests that verify the wrong behavior ;
- documentation that does not match implementation.

These risks are especially serious for a Secret Manager.

MCP Secret Manager protects secrets, permissions, tokens, audit records and cryptographic workflows. Security cannot rely on generated output alone.

The project therefore needs explicit AI governance.

The goal is not to avoid AI. The goal is to use AI safely, consistently and accountably.

## Decision

MCP Secret Manager adopts AI-First Governance.

This means AI assistance is allowed and encouraged, but governed by explicit rules.

Principles:

- humans remain decision-makers ;
- documentation has priority ;
- ADRs document structural decisions ;
- AI assists but does not govern ;
- every important change must be justified ;
- generated code must be reviewed ;
- tests remain mandatory ;
- security is never delegated to a model ;
- assumptions must be explicit ;
- architecture boundaries must be respected.

### Human responsibility

Humans are responsible for:

- final architectural decisions ;
- accepting or rejecting Pull Requests ;
- security judgment ;
- release decisions ;
- incident response ;
- changes to governance ;
- approving sensitive changes.

AI output may inform these decisions, but does not replace them.

### AI responsibility

AI assistants may:

- analyze ;
- propose ;
- draft ;
- implement ;
- test ;
- document ;
- review ;
- identify inconsistencies.

AI assistants must:

- follow the documentation ;
- state assumptions ;
- keep changes small ;
- avoid hidden behavior ;
- respect the architecture ;
- report uncertainty ;
- avoid inventing contracts ;
- avoid weakening security.

### Documentation responsibility

Documentation is the source of truth.

AI assistants and human contributors must consult the relevant documents before making significant changes.

When documentation and implementation conflict, the conflict must be resolved explicitly.

### Code responsibility

Code implements documented decisions.

Generated code has no special status. It must satisfy the same requirements as human-written code:

- tests ;
- review ;
- documentation ;
- security ;
- maintainability ;
- architecture compliance.

### Review responsibility

Review validates that a change is safe, coherent and aligned with the project.

AI review may assist, but human review remains required for sensitive changes.

### Test responsibility

Tests remain mandatory.

AI-generated tests must be reviewed like any other tests.

Passing tests are not sufficient if the tests validate the wrong behavior.

## Alternatives considered

### Fully manual development

Advantages:

- more traditional process ;
- clearer human authorship ;
- fewer AI-specific risks ;
- easier to reason about responsibility.

Disadvantages:

- slower documentation and analysis ;
- less leverage for repetitive work ;
- fewer automated consistency checks ;
- misses the project's AI-first working model ;
- less realistic for the intended development workflow.

Reason not retained:

MCP Secret Manager intentionally uses AI assistance. Avoiding AI entirely would reduce leverage and conflict with the project's development philosophy.

### AI without governance

Advantages:

- fastest apparent development ;
- low process overhead ;
- easy generation of code and docs ;
- fewer rules for contributors.

Disadvantages:

- high risk of hallucinated behavior ;
- architecture drift ;
- undocumented assumptions ;
- inconsistent quality ;
- security regressions ;
- difficult reviews ;
- technical debt ;
- loss of trust.

Reason rejected:

Ungoverned AI assistance is unacceptable for a Secret Manager. Speed without traceability is a liability.

### AI as decision-maker

Advantages:

- rapid decisions ;
- reduced human coordination ;
- possible automation of routine choices ;
- scalable assistance.

Disadvantages:

- unclear accountability ;
- models can be wrong ;
- security judgment cannot be delegated ;
- decisions may be based on incomplete context ;
- difficult governance ;
- unacceptable risk for critical systems.

Reason rejected:

AI may recommend decisions, but humans must remain accountable. MCP Secret Manager cannot delegate governance to a model.

### Optional documentation

Advantages:

- faster implementation ;
- less writing ;
- lower contribution barrier ;
- easier for small changes.

Disadvantages:

- decisions become implicit ;
- AI assistants lose source-of-truth context ;
- future contributors lose rationale ;
- review quality decreases ;
- architecture drift increases ;
- security assumptions become hidden.

Reason rejected:

Documentation is part of the project's governance and security model. It cannot be optional for significant changes.

### Validation only by tests

Advantages:

- objective pass/fail signal ;
- automation-friendly ;
- useful for CI ;
- catches many regressions.

Disadvantages:

- tests can be incomplete ;
- tests may assert wrong behavior ;
- tests do not explain architectural intent ;
- tests do not replace security review ;
- tests do not document trade-offs ;
- tests do not prevent all AI hallucinations.

Reason rejected:

Tests are mandatory, but not sufficient. MCP Secret Manager also requires documentation, review and explicit decisions.

## Consequences

### Positive consequences

AI-First Governance provides:

- better quality ;
- better coherence ;
- traceable decisions ;
- more reliable AI assistance ;
- stronger security ;
- durable documentation ;
- easier onboarding ;
- clearer review expectations ;
- lower risk of AI-driven drift ;
- better long-term maintainability.

### Negative consequences

This decision also has costs:

- more demanding process ;
- mandatory reviews ;
- documentation maintenance ;
- discipline required ;
- slower acceptance of sensitive changes ;
- contributors must understand governance documents.

These costs are accepted.

## Trade-offs

AI can increase development speed significantly.

That speed must be balanced by strong governance.

The goal is to augment developers, not replace their judgment.

AI assistants are useful for drafting, checking, exploring and accelerating work. They are not accountable maintainers.

Strong governance improves long-term quality because it:

- reduces hallucinated behavior ;
- keeps decisions traceable ;
- makes reviews easier ;
- aligns AI output with project rules ;
- protects architecture ;
- protects security guarantees ;
- preserves trust.

The project should use AI confidently, but never casually.

## Related Documents

- `docs/AI_RULES.md`
- `docs/CONSTITUTION.md`
- `docs/CONTRIBUTING.md`
- `docs/TESTING.md`
- `docs/PROJECT.md`
- `docs/adr/ADR-0001-clean-architecture.md`
- `docs/adr/ADR-0002-postgresql-primary-storage.md`
- `docs/adr/ADR-0003-envelope-encryption.md`
- `docs/adr/ADR-0004-rest-mcp-dual-interface.md`
- `docs/adr/ADR-0005-rbac-authorization-model.md`
- `docs/adr/ADR-0006-documentation-first-development.md`
- `docs/adr/ADR-0007-openclaw-first-mvp.md`

## Future evolution

AI governance may evolve toward:

- specialized agents ;
- automated review ;
- documentation generation ;
- architecture verification ;
- assisted security analysis ;
- AI-assisted CI ;
- migration analysis agents ;
- QA agents ;
- performance analysis agents.

These evolutions must always:

- keep a human as final responsible party ;
- preserve traceability of decisions ;
- respect documentation as the source of truth ;
- maintain security requirements ;
- remain compatible with existing ADRs ;
- keep generated output reviewable ;
- avoid hidden behavior ;
- preserve accountability.

Any major change to AI governance must be documented in a new ADR and reflected in `docs/AI_RULES.md`.

