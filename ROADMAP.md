# AgentGate — Roadmap

Single source of truth for what we're building and in what order. Each phase links to a
**detailed SPEC**. The context behind it all: [docs/00-BACKGROUND.md](docs/00-BACKGROUND.md)
· [docs/01-MARKET.md](docs/01-MARKET.md).

**Product:** the action firewall + accountability ledger for agents-that-act.
**First wedge:** a PR firewall for human + AI-agent code changes.

## Phases

| # | Stage | Outcome | Definition of Done (a runnable check) | Status | Spec |
|---|-------|---------|----------------------------------------|--------|------|
| 0 | Core gate | Offline pipeline: verify → classify → check → decide → audit | `make check` green (25 tests, lint); live `401`/`202` | ✅ Done | [phase-0](docs/specs/phase-0-core-gate.md) |
| 1 | Live GitHub loop | Gate acts on a real repo; human-approval loop; the "catch-it-live" demo | E2E on a test repo: agent PR blocked/escalated + audit verifies | 🚧 In progress — code-complete + offline-verified (42 tests); live-repo E2E pending creds | [phase-1](docs/specs/phase-1-github-loop.md) |
| 1.5 | Non-bypassable enforcement | The gate is the *only* merge path; protect the gate from the code it judges; robust actor identity | `audit-repo` reports every bypass gap; evaluator-error → merge-blocking verdict; self-approval refused | 🎯 Next after P1 | [phase-1.5](docs/specs/phase-1.5-non-bypassable.md) |
| 2 | Trust & compliance | Audit export + **external anchoring (WORM/timestamp)** + policy library + LLM reviewer + metrics | Signed report; chain head corroborated by an external anchor (operator-tamper detectable) | 🚧 Started — **Ed25519 chain-head signing landed** ([ADR-003](docs/adr/003-ed25519-audit-signing.md)); external anchoring + export next | [phase-2](docs/specs/phase-2-trust-compliance.md) |
| 3 | General action firewall | Beyond PRs: gate any consequential action via a proxy/MCP shim | A non-GitHub action (mock payment) gated + audited via the same core | ⬜ Planned | [phase-3](docs/specs/phase-3-action-firewall.md) |
| 4 | Scale & GTM | Multi-tenant, SOC2 posture, pilots, pricing validation | Design-partner pilot live; buyer + pricing validated | ⬜ Planned | [phase-4](docs/specs/phase-4-scale-gtm.md) |

## How we work (the discipline)

The rules that keep planning honest and building fast — we dogfood our own gate:

1. **Spec before build.** Every phase (and any non-trivial change) has a SPEC in
   `docs/specs/` with an explicit **Definition of Done = a runnable check**, never a slide.
   The SPEC is the contract; the code proves it.
2. **Verification is the only truth.** Drive against the discovered check (`make check`),
   fix the named failure, re-run. An honest ❌ beats a fake ✅. Stubs raise, they don't lie.
3. **Single source of truth.** This file + the specs. Anything else (README, old docs)
   points here. Spec can't drift into two places.
4. **Decisions get recorded.** Irreversible/architectural calls → a short ADR in
   `docs/adr/` (template: `docs/adr/000-template.md`).
5. **Dogfood from Phase 1.** Once the live loop works, AgentGate reviews PRs *to this repo*
   (human + AI-agent authors). Our process is our demo.
6. **Small, single-purpose PRs.** Large diffs / protected-path touches escalate by design.

## Tracking

- **Now (solo + coding agents):** specs hold the task checklists; check them off in-file.
- **Once the remote exists:** promote each SPEC's checklist to **GitHub Issues** and a
  **Project board** (one column per phase). `AGENTS.md` tells agents the rules.
- Suggested labels: `phase:0..4`, `type:feat|fix|chore|spec`, `risk:high` (auto-escalated).
