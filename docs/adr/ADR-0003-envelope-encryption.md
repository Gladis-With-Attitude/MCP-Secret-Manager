# ADR-0003: Adopt Envelope Encryption

## Status

Accepted

## Date

YYYY-MM-DD

## Context

MCP Secret Manager is responsible for protecting secret values at rest.

A Secret Manager cannot safely rely on encrypting all secret values directly with a single long-lived key.

The project has several cryptographic constraints:

- protection of secrets at rest ;
- key rotation ;
- limitation of the blast radius after compromise ;
- separation of responsibilities ;
- auditability ;
- future evolution ;
- reasonable performance ;
- compatibility with future Secret Providers ;
- compatibility with future hardware or external key systems.

MCP Secret Manager stores encrypted values in PostgreSQL, but cryptography is an application responsibility.

PostgreSQL is responsible for persistence. It stores ciphertexts, cryptographic metadata and domain metadata. It must not be considered the component that enforces application-level encryption of secret values.

Database-native protections can help protect the database files or storage layer, but they do not provide the same guarantees as application-level encryption:

- they may not protect against a database dump ;
- they may not separate keys by secret or version ;
- they may not support application-level rotation semantics ;
- they may not bind ciphertexts to domain context ;
- they do not express Secret Manager-specific invariants.

Using a single key directly for all secret values would create serious risks:

- compromise of that key could expose every secret ;
- rotation would require re-encrypting all secret values directly ;
- blast radius would be maximal ;
- different vaults and versions would not be isolated ;
- future integration with KMS, HSM or external providers would be harder ;
- key lifecycle would be difficult to reason about ;
- audit and incident response would be less precise.

MCP Secret Manager needs a strategy that is simple enough for the MVP, but strong enough to support long-term cryptographic governance.

## Decision

MCP Secret Manager adopts Envelope Encryption.

The conceptual hierarchy is:

```text
Master Key
  -> Data Encryption Keys (DEK)
    -> Secret Values
```

In this model:

- secret values are encrypted with a DEK ;
- a DEK is protected by a Master Key or a key derived from the Master Key hierarchy ;
- PostgreSQL never stores plaintext secret values ;
- PostgreSQL may store ciphertexts ;
- PostgreSQL may store non-secret cryptographic metadata required for authorized decryption ;
- PostgreSQL may store wrapped or protected key material metadata as defined by the cryptographic design.

The MVP uses this model conceptually even if the first implementation is intentionally simple.

The design must preserve the following separation:

- business decisions remain in the Application Layer ;
- authorization happens before decryption ;
- cryptographic primitives are provided by Infrastructure ;
- Domain remains independent of concrete algorithms ;
- PostgreSQL persists encrypted state but does not own cryptographic policy.

The Application Layer coordinates when encryption and decryption are allowed.

The Infrastructure Layer provides concrete cryptographic operations.

The Domain Layer models Secret, SecretVersion and related invariants without depending on AES, key files, KMS, HSM or any specific crypto backend.

## Alternatives considered

### Single Master Key

Advantages:

- simpler initial implementation ;
- fewer cryptographic metadata fields ;
- easier mental model ;
- less key management logic ;
- faster prototype.

Disadvantages:

- maximum blast radius if the key is compromised ;
- difficult rotation ;
- no isolation by version ;
- no clean rewrap strategy ;
- harder future integration with KMS or HSM ;
- weaker incident response ;
- stronger coupling between all secrets and one key.

Reason rejected:

A single key directly encrypting all secret values is too risky for a Secret Manager. It does not provide the isolation, rotation path or long-term governance required by MCP Secret Manager.

### Plaintext storage

Advantages:

- simplest possible persistence ;
- easy debugging ;
- no cryptographic complexity.

Disadvantages:

- catastrophic security failure ;
- PostgreSQL dump exposes all secrets ;
- backups expose all secrets ;
- logs and queries become dangerous ;
- violates the core purpose of the project.

Reason rejected:

Plaintext storage is unacceptable. MCP Secret Manager must never store secret values in plaintext.

### Database-native encryption only

Advantages:

- can protect storage files ;
- may be transparent to the application ;
- can reduce operational risk for disk theft ;
- may be provided by existing infrastructure.

Disadvantages:

- does not necessarily protect database dumps ;
- does not provide per-secret or per-version key semantics ;
- does not enforce Secret Manager-specific cryptographic context ;
- does not solve application-level key rotation ;
- does not protect against privileged database access ;
- couples security guarantees to database deployment details.

Reason rejected:

Database-native encryption may be useful as defense in depth, but it is insufficient as the primary protection mechanism for secret values.

MCP Secret Manager needs application-level encryption.

### Client-side encryption only

Advantages:

- server may never see plaintext ;
- strong separation between client and server ;
- useful for some zero-knowledge systems ;
- reduces server-side exposure in some scenarios.

Disadvantages:

- complex key distribution ;
- difficult OpenClaw integration ;
- difficult MCP agent workflows ;
- server cannot help with rotation or provider operations ;
- harder search, metadata management and lifecycle control ;
- complicated recovery ;
- difficult to enforce consistent behavior across clients.

Reason rejected:

Client-side encryption may be useful for future advanced modes, but it is not appropriate as the MVP default. MCP Secret Manager must serve OpenClaw, MCP clients and service accounts with a consistent server-side security model.

### Hardware Security Module from the MVP

Advantages:

- stronger key protection ;
- non-exportable keys ;
- better production hardening ;
- improved resistance to key theft ;
- clear path for high-assurance deployments.

Disadvantages:

- higher operational complexity ;
- hardware or external service dependency ;
- harder local development ;
- more complex testing ;
- slower MVP ;
- not necessary for the first self-hosted personal deployment.

Reason deferred:

HSM support is valuable, but it should not be required in the MVP. Envelope Encryption prepares the project for HSM integration later without forcing that complexity immediately.

## Consequences

### Positive consequences

Adopting Envelope Encryption provides:

- better isolation ;
- easier key rotation ;
- reduced blast radius ;
- improved future evolution ;
- clearer separation of responsibilities ;
- compatibility with future Secret Providers ;
- better cryptographic governance ;
- clearer incident response ;
- future support for rewrap ;
- future support for external key systems.

### Negative consequences

This decision also has costs:

- more complex architecture ;
- additional cryptographic metadata ;
- key management requirements ;
- more failure modes ;
- future rotation logic ;
- more tests ;
- stricter documentation needs.

These costs are accepted because the project is a Secret Manager.

## Trade-offs

Envelope Encryption is more complex than encrypting every value with one key.

That complexity is acceptable because it directly improves the project's security posture and long-term maintainability.

Envelope Encryption is widely adopted in Secret Managers and key management systems because it separates data encryption from key protection. This separation enables rotation, rewrap, blast-radius reduction and integration with external key systems.

For MCP Secret Manager, Envelope Encryption naturally prepares:

- KMS integration ;
- HSM integration ;
- Cloud Secret Providers ;
- multiple Master Keys ;
- key rotation ;
- key rewrap ;
- vault-level cryptographic separation ;
- future crypto agility.

The MVP should keep the implementation simple, but it must not choose a design that prevents these capabilities later.

## Related Documents

- `docs/CRYPTOGRAPHY.md`
- `docs/SECURITY.md`
- `docs/DATABASE.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`
- `docs/adr/ADR-0001-clean-architecture.md`
- `docs/adr/ADR-0002-postgresql-primary-storage.md`

## Future evolution

Envelope Encryption allows the project to evolve toward:

- automatic Master Key rotation ;
- multiple Master Keys ;
- external Secret Providers ;
- HSM ;
- Cloud KMS ;
- TPM-backed key protection ;
- YubiKey-assisted operations ;
- advanced cryptographic policies ;
- rewrap operations ;
- multi-key support ;
- crypto agility.

These evolutions must never require changing:

- the Domain Layer ;
- core security invariants ;
- audit guarantees ;
- public contracts ;
- the requirement that authorization happens before decryption ;
- the requirement that plaintext secrets are never stored in PostgreSQL.

Any major change to the cryptographic hierarchy must be documented in a new ADR and reflected in `docs/CRYPTOGRAPHY.md`.

