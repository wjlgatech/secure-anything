# ADR 003 — Ed25519-sign the audit ledger (chain head + evidence export)

- **Status:** accepted (implemented 2026-07-18)
- **Date:** 2026-07-18
- **Deciders:** Paul Wu

## Context

Our ledger (`src/agentgate/audit.py`) is **hash-chained** only:
`hash = sha256(prev_hash | kind | canonical(payload))`. Re-walking the chain detects insertion,
deletion, or edit of history — *relative to a copy of the chain the verifier already trusts*.

It does **not** defend against the operator who controls the database: someone who can rewrite rows
can also recompute every downstream hash and present a self-consistent forged chain. Hash-chaining
proves *internal consistency*, not *authenticity*. Phase 2 explicitly calls for
"external anchoring (WORM/timestamp) … operator-tamper detectable" — that requirement is unmet by
chaining alone.

Prior art confirms the gap and the fix. The USC FORTIS Lab's **AEGIS**
([07-PRIOR-ART.md](../07-PRIOR-ART.md)) ships a strict superset of our audit crypto: trace
hash-chain **+** canonical content-hash **+ Ed25519 detached signatures** on self-verifiable evidence
packs (`gateway-mcp/src/services/signing.ts`, `sdk-python/agentguard/crypto/signing.py`). A SOC 2
auditor verifies their pack offline, without trusting the producer. We should match this.

Relevant SPEC: [phase-2-trust-compliance.md](../specs/phase-2-trust-compliance.md).

## Options considered

1. **Ed25519 detached signatures over chain heads + signed evidence export** — the gate holds a
   private key (PEM/PKCS8, `0o600`); it signs each new chain head (or periodic checkpoints) and can
   export a signed, self-contained evidence bundle (records + embedded public key + `key_id`).
   - *Pros:* defeats operator tampering (forging requires the private key, not just DB write);
     64-byte sigs / 32-byte keys keep exports compact; deterministic; native in Python `cryptography`
     and Node `crypto`; matches AEGIS so buyers/auditors see a familiar primitive; directly satisfies
     Phase-2 "operator-tamper detectable."
   - *Cons:* introduces key management (generation, storage, rotation) — a new secret to protect;
     a stolen key forges silently until rotation.
2. **RSA/ECDSA signatures** — same idea, different algorithm.
   - *Pros:* ubiquitous.
   - *Cons:* larger sigs/keys; no upside over Ed25519 for this use; AEGIS's own rationale (compact,
     deterministic, native) applies to us identically.
3. **External transparency log / RFC-3161 timestamping / public WORM anchor** — periodically publish
   the chain head to an append-only external service.
   - *Pros:* strongest — even a key thief can't rewrite already-anchored history.
   - *Cons:* adds an external dependency and network trust boundary; breaks our "offline-deterministic
     core" test discipline unless carefully seam-isolated. Heavier than the immediate need.

## Decision

Adopt **Option 1**: Ed25519 signing of chain heads plus a signed, self-verifiable evidence export,
as a new **seam** (`audit/signing.py`) so the pure core stays offline-testable (sign/verify run on
in-memory bytes; the key source is injectable, defaulting to a test key in tests). Keep **Option 3**
(external anchoring) as the *next* step layered on top — the signature makes the anchored value
authentic, the anchor makes it non-rewritable.

## Consequences

- **Easier:** Phase-2 "operator-tamper detectable" is satisfiable; evidence export becomes a signed
  artifact an auditor trusts offline; parity with the strongest prior-art primitive.
- **Harder:** we now own key lifecycle — generation, `0o600` storage, rotation policy, and a
  documented recovery story. Rotation must be recorded *in the ledger itself* (a `key_rotation` event)
  so the trust chain across keys is auditable.
- **Revisit:** whether to layer Option 3 (RFC-3161 / transparency log) in Phase 2/3; where the key
  lives in multi-tenant deployment (per-tenant vs platform key) — align with the AEGIS
  `gateway_config` persistence pattern.
## Implementation (2026-07-18)

Shipped in this change (56 tests, lint clean):

- **`src/agentgate/signing.py`** — `Signer` Protocol seam + `Ed25519Signer` body (lazy
  `cryptography` import so the app still loads without the dep; sign/verify over bytes; PKCS8
  PEM save/load at `0o600`). Landed as a flat module, not `audit/signing.py`, to avoid converting
  the `audit.py` module into a package (lower blast radius; same seam).
- **`AuditLedger(session, signer=None)`** — signs each chain head on `append()`; `verify()` /
  `verify_chain(events, signer=…)` now require a valid signature per event when a signer is present
  (a dropped signature = tampering). `signer=None` is unchanged, backward-compatible behaviour.
- **`AuditEvent.signature`** — new nullable column; unsigned chains leave it NULL.
- **`GET /audit/verify`** — returns `{"intact", "signed"}`; loads the signer from
  `AGENTGATE_AUDIT_KEY` (PKCS8 PEM path) via an isolated `_audit_signer()` so the pure ledger stays
  key-agnostic.
- **`cryptography>=42`** added to base dependencies.
- Test `test_signature_tamper_is_detected` proves the core value: an operator who rewrites a row
  **and recomputes the whole hash chain** passes chain-only verification but fails signature
  verification.

**Remaining follow-ups:** add `key_rotation` as an audited event kind (record rotations in the
ledger so the cross-key trust chain is auditable); spec the signed evidence-export bundle format in
the Phase-2 SPEC; decide per-tenant vs platform key placement; consider layering Option 3 (external
anchoring / RFC-3161) on top.
