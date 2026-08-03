# SPEC — Phase 0: Core Gate  (Status: ✅ Done)

## Goal
A complete, offline-testable evaluation pipeline: verify a webhook → classify the actor →
run deterministic checks → decide (actor-aware) → write a tamper-evident audit record.

## User stories
- As a platform owner, every PR (human or agent) is evaluated by one policy before merge.
- As a compliance owner, every decision is recorded in a tamper-evident log.
- As a developer, I can run the whole gate locally with no external services.

## In scope
Webhook HMAC verify; actor classification (human/ai_agent/bot); checks (secret scan,
protected paths, diff size); decision engine; hash-chained audit ledger; idempotent worker;
FastAPI + queue + SQLite/Postgres.

## Out of scope (later phases)
Live GitHub posting (P1), LLM reviewer (P2), Redis in prod (P1), multi-tenancy (P4).

## Design (as built)
See [../03-ARCHITECTURE.md](../03-ARCHITECTURE.md) and [../05-POLICY.md](../05-POLICY.md).
Key calls: policy-as-data; pure `evaluate()`/`decide()` with I/O at the edges; idempotency
on `delivery_id`; "no evidence ⇒ escalate".

## Definition of Done ✅
`make check` green (25 tests + ruff); live smoke: unsigned webhook → `401`, signed PR →
`202 queued` with correct actor kind.

## Shipped
Commit `c6e725c`. Modules under `src/secure_anything/organs/agentgate/`; tests under `tests/`.
