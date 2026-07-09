# 02 — Roadmap

Phased so each stage ships a demoable, verifiable increment. "Done" = a check you can run.

## Phase 0 — Core gate (DONE ✅)

The spine, offline-testable end to end.
- Webhook HMAC verification · actor classification (human/ai_agent/bot) · deterministic
  checks (secret scan, protected paths, diff size) · actor-aware decision engine ·
  hash-chained audit ledger · idempotent job processing · FastAPI + queue + Postgres/SQLite.
- **Gate:** `make check` (25 tests, lint) green; live `401`/`202` verified.

## Phase 1 — Real GitHub loop (MVP, "catch it live")

Make it act on a real repo.
- GitHub App: installation-token minting; post **check-runs** (block merge) + **reviews**
  (approve / request-changes) + a comment explaining the decision and linking the audit id.
- Worker on Redis; `fetch_changeset` live; handle `synchronize` re-runs.
- **Human approval loop:** an "Approve" affordance (comment command / lightweight web view)
  that records approver identity + timestamp into the ledger.
- **Demo:** an agent PR that (a) plants a secret, (b) rewrites CI, (c) lands a 4k-line diff —
  each caught, routed, logged. Record the clip.
- **Gate:** end-to-end on a live test repo; audit chain verifies.

## Phase 2 — Trust & compliance layer

Turn the ledger into a product.
- Immutable **audit export** (EU AI Act / FINRA-shaped report) + `audit/verify` attestation.
- Policy library + per-repo/per-org policy overrides; policy change requires approval.
- LLM risk reviewer wired (Claude) with a rubric; "no evidence => escalate" enforced.
- Metrics: auto-approve rate, escalation rate, mean-time-to-approve, catches by type.
- **Gate:** a signed compliance report generated from real history.

## Phase 3 — Beyond PRs: the general action firewall

Generalize from "PR" to "any consequential action."
- A thin **action-proxy SDK/MCP shim**: agents route tool calls (refund, DB write, email,
  A2A request) through the same policy → approve / deny / escalate → audit.
- Consume external **agent identity** (Cisco Duo / Okta / MCP auth) instead of inferring it.
- Scoped, short-lived, revocable per-action credentials (delegation-chain aware).
- **Gate:** a non-GitHub action (e.g. a mock payment) gated + audited through the same core.

## Phase 4 — Scale & GTM

- Multi-tenant, SOC2 posture, HA workers, rate limiting, per-org KMS for secrets.
- Design-partner pilots (teams running 10–50 coding agents daily).
- Pricing validation (per-seat vs. per-gated-action vs. compliance tier).

## Guardrails on ourselves

- Every phase ends with a runnable check, not a slide.
- No silent caps or fake passes; stubs raise, they don't lie.
- Validate the **buyer** and **$ TAM** (see [01-MARKET.md](01-MARKET.md)) before Phase 4 spend.
