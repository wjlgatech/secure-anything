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
2. **Policy management**: per-org/per-repo overrides layered on defaults; policy changes
   require human approval (they already hit a protected path).
3. **LLM reviewer**: wire the Anthropic client behind `review/llm_review.py` with a rubric
   returning structured risk + concerns; enforce "no evidence ⇒ escalate".
4. **Metrics**: counters + a `/metrics` endpoint (Prometheus) and a simple dashboard.

## Out of scope
Non-GitHub actions (P3), SOC2/multi-tenant hardening (P4).

## Task checklist
- [ ] Report generator + signing; attestation includes ledger head hash.
- [ ] Layered policy resolution (org → repo → default) + change-approval flow.
- [ ] LLM reviewer: prompt/rubric, structured output, timeout/fallback → escalate.
- [ ] Metrics instrumentation + dashboard.
- [ ] Tests: report determinism, policy layering, reviewer fallback → escalate.

## Definition of Done
A signed compliance report is generated from real decision history, `audit/verify` returns
`intact: true`, and the LLM reviewer's unavailability provably escalates a risky PR (test).

## Risks / open questions
- Report format buyers actually accept (validate with a design partner).
- LLM reviewer cost/latency at 50 PRs/day; cache by diff hash.
