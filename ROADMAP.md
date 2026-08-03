# ROADMAP — secure-anything

The milestone **arc** for the meta-repo. Charter: [docs/VISION.md](docs/VISION.md) ·
Contract: [GOAL.md](GOAL.md) · Doctrine: [docs/META_REPO_PLAYBOOK.md](docs/META_REPO_PLAYBOOK.md).

Each row's Definition of Done is **a runnable check**, never a slide. Score with
`anyagent analyze .` at every milestone and record the trajectory honestly.

**North star: Verified Control Coverage (VCC)** — `python3 scripts/northstar.py`.
A milestone that ships mechanics without moving VCC is logged as *maintenance, not progress*.

## The arc

| # | Milestone | Outcome | Definition of Done (runnable) | Status |
|---|---|---|---|---|
| **M0** | **Foundation — born green** | Charter + lean core + spec-as-data + gates + flagship skill; AgentGate demoted to an organ with zero test loss | `make check` exit 0: ruff + all tests + manifest gate + build drift-check + self-audit ≥90 + every eval routing case a test. G1–G4, G7 in [GOAL.md](GOAL.md) pass | 🚧 In progress |
| **M1** | **Coverage — the rich ecosystem** | Every ⚪ candidate becomes 🟡 digested: pinned SHA, license, verified facts, evidence tier. Six entry classes populated | G5 passes: ≥40 entries, ≥6 classes, `verified_at` on each, **zero** unverified factual claims (`scripts/verify_registry.py`) | ⬜ Next |
| **M2** | **Proof — the first chain** | One cross-capability chain run live end-to-end: scan → gate seam → signed ledger receipt | `docs/walkthroughs/<chain>.md` exists, manifest-gated, carrying **verbatim** exit codes; the satellite's own gate ran here (exit 0); **VCC > 0** | ⬜ |
| **M3** | **Control mapping** | Every gate finding cites a control (OWASP LLM / OWASP Agentic / MITRE ATLAS / NIST AI RMF) | `data/controls.yml` is the single source; every 🟢 capability maps to ≥1 control; VCC computable and reported in README (drift-gated) | ⬜ |
| **M4** | **Library + bounded autonomy** | N chains with golden examples banked from real runs; AI-autonomous mode unlocked for chains that have one | Each chain: walkthrough + eval case + test. Autonomy allowed only where a golden example exists; every irreversible step still human-gated | ⬜ |
| **M5** | **Cadence** | Weekly freshness sync (STALE measured, human-gated PRs); the ecosystem stops rotting | A scheduled workflow with a **verified scheduled run** (`event == "schedule"` AND `conclusion == "success"`); failure opens an issue; the job detects its own absence | ⬜ |

## Organ roadmaps

The meta-repo composes; the organs do the domain work and keep their own arcs.

- **AgentGate** (PR firewall, Ed25519 audit-of-record) — [docs/organs/agentgate/ROADMAP.md](docs/organs/agentgate/ROADMAP.md).
  Phases 0–4 continue unchanged; Phase 1.5 (non-bypassable enforcement) is still the next
  product-critical step and is **not** blocked by the meta work.

## How we work (the discipline)

Inherited from AgentGate, extended by the meta laws. We dogfood our own gate.

1. **Spec before build.** Every milestone has a runnable DoD. The spec is the contract; the code
   proves it.
2. **Verification is the only truth.** Drive against `make check`, fix the named failure, re-run.
   An honest ❌ beats a fake ✅. Stubs raise, they never lie.
3. **Spec is data.** `data/*.yml` is the single source; every published surface (README blocks,
   `skills/secure-anything/SKILL.md`) is **generated** and drift-gated by `scripts/build.py --check`.
4. **The status ladder is the product.** ⚪ candidate → 🟡 digested (facts pinned to a SHA,
   unconfirmed labeled) → 🟢 integrated (its gate ran *here*, exit code recorded). A validator
   refuses a promotion whose on-disk evidence is missing.
5. **Aggregate exit codes, never claims.** No evidence ⇒ *not measured* ⇒ excluded. A blocking
   gate can never pass on unmeasured items.
6. **Satellites, never vendored.** Pointer + pinned SHA + digest. AGPL/unlicensed ⇒ pointer only,
   run upstream.
7. **Decisions get recorded.** Architectural/irreversible calls → an ADR in `docs/adr/`.
8. **Benchmark numbers obey eval-anything's non-negotiables** — strict scoring, false-escalation
   as the never-degrade guardrail, error bars on deltas, every red-team result names its
   attack-set version.
