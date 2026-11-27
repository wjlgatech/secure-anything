# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

**secure-anything** is a **meta-repo**: the composition layer for agent security. It owns
**no domain logic**. Its product is a verified composition — a registry of capabilities, a
deterministic router, a uniform gate seam, a tamper-evident ledger, and a computable north star.

Charter: `docs/VISION.md` · Contract: `GOAL.md` · Arc: `ROADMAP.md` · Doctrine:
`docs/META_REPO_PLAYBOOK.md` · Contributor rules: `AGENTS.md`.

**It was AgentGate until 2026-08-03** ([ADR-005](docs/adr/005-meta-repo-restructure.md)).
AgentGate survives in full as the first **organ** — see `docs/organs/agentgate/`.

## Commands

```bash
make install     # pip install -e ".[dev]"  (Python >=3.11)
make check       # THE canonical gate; CI runs exactly this
make northstar   # Verified Control Coverage, computed offline from data/
make receipts    # every run receipt is in the signed, hash-chained ledger (offline; in check)
python3 scripts/receipt.py run --capability <id> --target <owner/repo@sha> --tool-version <v> \
    [--report <file>] -- <command>          # run a tool and record its receipt
make route Q="scan my repo"   # drive the deterministic router
make build       # regenerate every published surface from data/
make run         # AgentGate organ: uvicorn on :8099
```

Run a single test: `python -m pytest tests/test_gate_seam.py::test_name -q`
(`pyproject.toml` sets `pythonpath = ["src"]`, so tests import without install.)

`make check` = ruff · charter manifest · registry evidence · receipts · build drift ·
self-audit (≥90) · pytest. **Never weaken a test or a budget to make it pass** — an honest ❌ beats a fake ✅.

## Architecture — three layers, one direction

```
data/*.yml                  ← THE single source of truth (spec-as-data)
  registry.yml    capabilities: organs, family repos, external satellites
  knowledge.yml   papers · books · blogs · people · labs · standards · concepts (evidence-tiered)
  controls.yml    OWASP LLM Top 10 + OWASP Agentic Top 10 — the north-star denominator
  ainative.yml    the disciplines the repo audits itself against

src/secure_anything/        ← THE LEAN CORE (<=600 LOC, budget-gated)
  spec.py       typed loaders for data/*.yml
  router.py     deterministic, word-bounded intent -> hand-off (no LLM)
  gate.py       GateResult / Aggregate — exit codes, never claims
  coverage.py   Verified Control Coverage (the north star)
  ledger.py     hash-chained record  |  store.py  ORM base  |  signing.py  Ed25519 (ADR-003)
  organs/agentgate/   ← the PR firewall: domain logic lives HERE, never in the core

scripts/                    ← thin checkers over the engine (maker is not the checker)
skills/secure-anything/     ← the flagship super-tool — GENERATED, drift-gated
eval/secure-anything.md     ← every routing claim, parsed into pytest cases
```

**Dependency direction is one-way: organ → core.** Never the reverse.

## Invariants (these govern behaviour — respect them)

- **Lean core is a budget with a test.** `test_core_is_lean` fails above 600 LOC;
  `test_core_never_imports_an_organ` and `test_core_names_no_vendor_or_protocol` enforce the rest.
  If you need domain knowledge, you are in the wrong layer — add an organ or a satellite.
- **Spec is data, generated surfaces are output.** Never hand-edit a `<!-- BEGIN GENERATED -->`
  block or `skills/secure-anything/SKILL.md`. Change `data/`, run `make build`.
- **The status ladder is the product.** ⚪ candidate → 🟡 digested (pinned SHA + digest) → 🟢
  integrated (its gate ran HERE, receipt in `runs/<id>/`). Only 🟢 moves the north star;
  `scripts/verify_registry.py` refuses promotions lacking on-disk evidence.
- **Aggregate exit codes, never claims.** No evidence ⇒ `NOT_MEASURED` ⇒ excluded and named. A
  blocking aggregate can never be green while something is unmeasured.
- **Verify, never recall.** Every external fact in `data/` is read from an API or a primary
  source and stamped `verified_at`. Unread ⇒ tier it `claimed`/`disputed` and label it.
- **Unresolved licence ⇒ pointer only.** `NOASSERTION` means restrictive: never vendor, never run
  it in our CI, never mark it integrated.
- **Satellites are never vendored.** Pointer + pinned SHA + digest, or nothing.
- **Checks are deterministic and offline.** No network, no API key in `make check`.
- **No silent stubs.** Unimplemented paths raise `NotImplementedError`.
- **Everything consequential appends to the ledger** (`secure_anything.ledger`).
- **A receipt is produced, never written.** Only `scripts/receipt.py run|record` creates files under
  `runs/`; it captures the OS exit code and parses counts from the tool's own report. Receipts are
  append-only and chained in `runs/ledger.jsonl`, signed with the machine-local key
  `~/.secure-anything/receipts-ed25519.pem` (public half `runs/receipts.pub`). Raw tool reports
  never enter the repo (they quote private source); receipts pin them by sha256.
- **Promote to 🟢 only when the run measured the target.** A firewall challenge page, a coverage
  limit or a tool error is a receipt, not a measurement (`nuclei` stays 🟡 for this reason).

## Adding things

- **A capability:** one row in `data/registry.yml` (⚪) → `docs/satellites/<id>.md` + `pinned_sha`
  (🟡) → a run receipt in `runs/<id>/` (🟢). If it costs more, the core has leaked.
- **A knowledge card:** `data/knowledge.yml` with an evidence tier + `verified_at`.
- **A routing claim:** a row in `eval/secure-anything.md` — it becomes a pytest automatically.
- **A check in the AgentGate organ:** see `docs/organs/agentgate/README.md`.

## Current status

**First receipts (2026-11-26, v0.3.0).** Seven capabilities are 🟢 integrated with signed run
receipts in `runs/` (trufflehog, gitleaks, semgrep, trivy, osv-scanner, claude-code-security-review,
skillspector); the live VCC is the generated block in README.md (`make northstar`). `nuclei` ran but
was answered by Vercel's firewall, so it stays 🟡. Deferred for money or long agent sessions:
codex-security, strix, pyrit, the SkillSpector LLM stage, cloudflare-security-audit-skill (costs in
CHANGELOG.md). AgentGate's Phase 1.5 continues in parallel.
