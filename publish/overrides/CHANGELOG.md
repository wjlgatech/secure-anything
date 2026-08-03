# Changelog

## 0.2.0 — 2026-08-03 — first public release

The composition layer for agent security, opened. This is a fresh public history: the layer was
developed privately and only the composition core plus the curated ecosystem are published, so
this repo starts clean rather than exposing unrelated history.

### The core (`src/secure_anything/`, 595 LOC, budget-gated)
- `spec.py` typed loaders for `data/*.yml` · `router.py` deterministic word-bounded routing
  (no LLM) · `gate.py` the `GateResult`/`Aggregate` seam · `coverage.py` the north star ·
  `ledger.py` + `store.py` + `signing.py` a hash-chained, optionally Ed25519-signed record.
- Leanness is a test, not a wish: `test_core_is_lean` (≤600 LOC),
  `test_core_never_imports_an_organ`, `test_core_names_no_vendor_or_protocol`.

### The ecosystem (`data/`)
- **31 capabilities** — scanners, guardrails, red-team, benchmarks, policy, threat modelling,
  provenance, protocols. Every star count, licence and push date read from the GitHub API on
  2026-08-03.
- **34 knowledge cards** — 8 papers (all resolved through the arXiv API), 2 books, 2 blogs,
  6 people, 5 labs, 4 standards, 4 concepts, plus deliberately-kept `claimed` and `disputed`
  cards.
- **20 controls** — OWASP Top 10 for LLM Applications (2025, `verified`) and OWASP Top 10 for
  Agentic Applications (2026, `corroborated`, honestly tiered because the primary is a PDF).

### The gates
- `make check` = ruff · charter manifest · registry evidence · generated-surface drift ·
  self-audit (≥90) · pytest. CI runs exactly `make check`, never a subset.
- `scripts/verify_registry.py` refuses any status promotion lacking on-disk evidence.
- `eval/secure-anything.md` — 26 routing cases, each a pytest, including the refusals and the
  deliberate no-match gaps.

### Honest edges at first release
VCC is **0/20 (0%)**: nothing has an integrated run receipt yet. 17 controls are *mapped* but
unproven; 3 (LLM08, LLM10, ASI08) have no capability at all. Those gaps are published rather
than hidden, and they are the roadmap.
