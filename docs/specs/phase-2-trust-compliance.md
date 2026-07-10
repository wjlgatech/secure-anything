# SPEC — Phase 2: Trust & Compliance Layer  (Status: ⬜ Planned)

## Goal
Turn the audit ledger into a product: exportable, attestable compliance evidence, a real
policy library, the LLM risk reviewer wired in, and operating metrics.

## User stories
- As a compliance owner, I can export a signed, tamper-evident report of every agent
  decision for an audit window (EU AI Act / FINRA shaped).
- As a platform owner, I manage policy per org/repo and every policy change is itself gated.
- As an eng lead, I see auto-approve rate, escalation rate, mean-time-to-approve, catches
  by type.

## In scope
1. **Audit export**: signed report (JSON + human PDF/MD) over a date range; embeds the chain
   attestation from `audit/verify`.
2. **External audit anchoring** (the honest "tamper-proof" claim). A hash chain alone is only
   tamper-evident *to us* — the operator controls both the app and the log and could rewrite
   the whole chain. To be credible to an auditor who distrusts the vendor, anchor the chain
   **outside our own control**, cheapest-first:
   - **WORM storage** — write the ledger (or periodic chain heads) to **S3 Object Lock in
     Compliance mode** on a write-isolated path (not even root can delete/overwrite before
     retention expires); maps directly to EU AI Act Art. 12 retention.
   - **RFC 3161 trusted timestamps** on each published chain head (proves existence-at-time
     independent of our clock — same reason Sigstore added a TSA).
   - **Public transparency log** (Merkle-based, à la Sigstore Rekor / Trillian) *if/when* a
     buyer needs third-party verifiability with inclusion proofs.
3. **Policy management**: per-org/per-repo overrides layered on defaults; policy changes
   require human approval (they already hit a protected path).
4. **LLM reviewer**: wire the Anthropic client behind `review/llm_review.py` with a rubric
   returning structured risk + concerns; enforce "no evidence ⇒ escalate".
5. **Metrics**: counters + a `/metrics` endpoint (Prometheus) and a simple dashboard.

## Out of scope
Non-GitHub actions (P3), SOC2/multi-tenant hardening (P4).

## Task checklist
- [ ] Report generator + signing; attestation includes ledger head hash.
- [ ] Audit anchoring: WORM/S3 Object Lock writer (write-isolated) + RFC 3161 timestamp on chain heads; a `verify` path that checks the external anchor, not just the internal chain.
- [ ] Layered policy resolution (org → repo → default) + change-approval flow.
- [ ] LLM reviewer: prompt/rubric, structured output, timeout/fallback → escalate.
- [ ] Metrics instrumentation + dashboard.
- [ ] Tests: report determinism, policy layering, reviewer fallback → escalate, anchor-mismatch is detected.

## Definition of Done
A signed compliance report is generated from real decision history; `audit/verify` returns
`intact: true` **and** the report's chain head is corroborated by an external anchor (WORM +
timestamp) so tampering by the operator is detectable, not just tampering by an outsider; and
the LLM reviewer's unavailability provably escalates a risky PR (test).

## Risks / open questions
- Report format buyers actually accept (validate with a design partner).
- LLM reviewer cost/latency at 50 PRs/day; cache by diff hash.
- Anchoring cost/latency and which anchor buyers actually require (WORM may satisfy most;
  transparency-log is heavier — don't build it until a buyer needs inclusion proofs).
