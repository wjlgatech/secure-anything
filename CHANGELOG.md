# Changelog

## 0.2.0 — 2026-08-03 — AgentGate becomes secure-anything (M0: born green)

The repo becomes a **meta-repo**: a lean composition core over a rich ecosystem. AgentGate is
retained in full as its first organ. See [ADR-005](docs/adr/005-meta-repo-restructure.md).

### Added — the charter
- `docs/VISION.md` — vision, mission, the computable north star (**Verified Control Coverage**),
  operating modes, non-goals, privacy declared PRIVATE on day one.
- `GOAL.md` — the founding intent recompiled into 7 machine-verifiable goals. "Really lean" is
  now 600 LOC with a test; "really rich" is coverage across 6 entry classes with zero unverified
  claims.
- `ROADMAP.md` — the milestone arc M0→M5. AgentGate's phase table moved to
  `docs/organs/agentgate/ROADMAP.md`, unchanged.

### Added — spec-as-data (`data/`)
- `registry.yml` — 31 capabilities across scanners, guardrails, red-team, benchmarks, policy,
  threat-modelling, provenance and protocols. Every star/license/push-date read from the GitHub
  API on 2026-08-03, never recalled.
- `knowledge.yml` — 34 evidence-tiered cards: 8 papers (all resolved through the arXiv API),
  2 books, 2 blogs, 6 people, 5 labs, 4 standards, 4 concepts, plus deliberately-kept `claimed`
  and `disputed` cards.
- `controls.yml` — OWASP Top 10 for LLM Apps (2025, `verified`) + OWASP Top 10 for Agentic
  Applications (2026, `corroborated`, honestly tiered because the primary is a PDF download).
- `ainative.yml` — 15 disciplines, each with an executable check.

### Added — the lean core (`src/secure_anything/`, 595 LOC, budget-gated)
- `spec.py` typed loaders · `router.py` deterministic word-bounded routing · `gate.py` the
  GateResult/Aggregate seam · `coverage.py` the north star · `store.py` + `ledger.py` +
  `signing.py` (the hash-chained, Ed25519-signed record, lifted from the organ into the core
  because the record must outlive any organ).

### Added — gates
- `make check` = ruff · charter manifest · registry evidence · build drift · self-audit · pytest.
  CI now runs exactly `make check` rather than a subset.
- `scripts/verify_registry.py` refuses any promotion lacking on-disk evidence — it refused both
  🟡 claims on first run until their digests were written.
- `scripts/ainative.py` self-audit: **100/100**.
- `eval/secure-anything.md` — 26 routing cases, each a pytest, including the refusals and the
  gaps.

### Fixed
- **Fail-open policy fallback** ([ADR-004](docs/adr/004-fail-closed-policy-fallback.md)): a
  missing policy document fell back to a bare `Policy()`, which protects nothing — so an
  AI-agent PR touching a protected path **auto-approved**, contradicting ADR-002. The fallback is
  now `Policy.strict()` (deny-by-default), the policy path resolves from `__file__` instead of a
  CWD-relative string, and `tests/test_policy_fail_closed.py` pins it.
- **Over-broad router trigger:** the trigger `book` matched "book me a flight to tokyo". Routing
  is now word-bounded (so `opa` no longer fires on "opaque") and the generic trigger was removed.
- **Archived upstream:** the registry records `microsoft/PyRIT`, not the archived `Azure/PyRIT` —
  caught by API verification.

### Changed
- `agentgate.*` → `secure_anything.organs.agentgate.*`. 56 pre-existing tests kept green
  throughout; the suite is now **122 tests**.
- Nothing was deleted: AgentGate's full README moved to `docs/organs/agentgate/README.md`.

### Honest edges at this milestone
VCC is **0/20 (0%)** — nothing has an integrated run receipt yet. 17 controls are *mapped* but
unproven; 3 (LLM08, LLM10, ASI08) have no capability at all. That gap is the M1/M2 queue.

## 0.1.0 — 2026-07-09 — AgentGate Phase 0/1
See [docs/organs/agentgate/README.md](docs/organs/agentgate/README.md) for the original history.
