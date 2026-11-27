# Changelog

## 0.3.0 — 2026-11-26 — first receipts: VCC leaves zero, only by what ran

The 12-tool list from a LinkedIn post (names treated as claims) was resolved against the GitHub API,
added to the registry, and every tool that could run here without a paid key was run against
Paul's own repos, site and skills. The north star moved only through signed run receipts.

### Added
- **`scripts/receipt.py`** — `run` executes a tool and records the exit code the OS returned,
  hashes of its stdout/stderr/report, and counts parsed from the tool's own report (`PARSERS`);
  `record` files a run observed elsewhere (CI) as `observed: remote`; `verify` re-derives the chain.
  Receipts land in `runs/<id>/`, each appended to `runs/ledger.jsonl` (the core's `compute_hash`)
  and Ed25519-signed (the core's `Ed25519Signer`); public key `runs/receipts.pub`, private key
  machine-local. No core change: the core stays at its 600-line budget.
- **`make receipts`** (in `make check`, offline) and `tests/test_receipts.py` (8): an edited exit
  code, a dropped ledger line, a hand-dropped receipt and a second signing key each fail.
- **Registry: 10 new capabilities** — `trufflehog`, `gitleaks`, `trivy`, `osv-scanner`, `nuclei`,
  `skillspector`, `cloudflare-security-audit-skill`, `strix`, `infisical`, `comp-ai` — plus refreshed
  metadata for `semgrep`, `claude-code-security-review`, `codex-security`, `pyrit`. Two new roles
  (`secrets`, `compliance`) in the generated tables. 8 new digests in `docs/satellites/`.
  8 new routing claims in `eval/secure-anything.md`.
- **Promoted to 🟢 integrated (receipts in `runs/`):** trufflehog, gitleaks, semgrep, trivy,
  osv-scanner, claude-code-security-review, skillspector.

### What the runs found (receipts in `runs/`; raw reports kept outside the repo)
- **Secrets: none.** TruffleHog over every ref of agentic-portfolio, ContentFactory and
  secure-anything: 0 results of any class. gitleaks: 11 hits, all false positives, each suppressed
  with a reason in the repo's `.gitleaksignore`.
- **Code:** Semgrep ERROR gate on agentic-portfolio: 2 → 0 (a `workflow_dispatch` input spliced
  into bash, fixed; a loopback CDP fetch, suppressed with a reason) — agentic-portfolio PR #594.
- **Dependencies:** agentic-portfolio prod critical 4 → 0 (Next.js 15.5.19 → 15.5.29, nodemailer
  9 → 10; PR #594); ContentFactory high 5 → 0 (wrangler 4.126 → 4.168; PR #24). Trivy 4 CRITICAL +
  44 HIGH → 4 HIGH; osv-scanner 129 → 34 advisories (agentic-portfolio), 30 → 0 (ContentFactory).
- **Live site:** Nuclei could not measure futuremake.io — 73 of 79 responses were Vercel's 403
  challenge page. `nuclei` stays 🟡.
- **Skills:** SkillSpector 2.13.7 (static, offline) over `~/.claude/skills`, one skill per run: 108 of 110 scanned (2 symlinks it refuses to follow), 6 CRITICAL / 4 HIGH. Hand triage of every CRITICAL/HIGH: all false positives (an API key sent to its own provider, a destination URL read from env, cleanup `rm -f`, a skill that quotes "ignore previous instructions" in order to forbid it) except one real low: `freellmapi` tells the agent to pipe a third-party install script into bash. A recursive scan of the folder had stopped at 17 skills (28.3% coverage, its own report), which is why it ran per skill.
- **CI added** to both family repos (`.github/workflows/security.yml`): TruffleHog, Semgrep (new
  ERROR only), dependency audit, advisory claude-code-security-review.

### Deferred — needs a paid key, a long agent session, or a production decision (cost = our estimate, not a vendor quote)
| tool | blocker | rough cost per run | would cover |
|---|---|---|---|
| `codex-security` | ChatGPT/Codex Security access or `OPENAI_API_KEY` (the OpenAI balance was 0 on 2026-11-26) | ~$10–50 per deep repo scan | LLM02, LLM03, LLM05, ASI05 |
| `strix` | `STRIX_LLM` + `LLM_API_KEY`, Docker; actively attacks the target — preview deploys only | ~$5–30 per scan (millions of tokens) | LLM05, ASI05 |
| `pyrit` | a target LLM endpoint + an attacker/scorer model | ~$1–5 per 100-prompt campaign, plus the target's quota | LLM01, LLM09, ASI01 |
| `skillspector` LLM stage | a provider key (its default is NVIDIA's; a free build.nvidia.com key may do) | $0–2 | deepens LLM01 |
| `cloudflare-security-audit-skill` | a multi-phase agent session per repo | hours of model time per repo | LLM02, LLM05, ASI05 |
| `claude-code-security-review` in ContentFactory | `ANTHROPIC_API_KEY` repo secret | ~$0.05–0.50 per PR | LLM02, LLM05 |
| `infisical` | NOASSERTION licence (MIT outside `ee/`); adopting it moves production secrets | $0 software, a migration | LLM02, ASI03 |
| `comp-ai` | self-hosted app + database; only useful when someone asks for SOC 2 evidence | $0 software, setup time | none of the OWASP controls |

### Investigated / Rejected
- **Promoting `nuclei` on its exit code 0:** rejected — 0 of 79 responses reached the app. A scan
  answered by a firewall is a receipt, not a measurement.
- **Writing receipts by hand from earlier shell runs:** rejected — every receipt is produced by
  `receipt.py`, which runs the tool itself. The first night's ad-hoc runs inform the triage only.
  Three receipts produced by a shell word-splitting mistake (a wrong path, exit 1 in one second)
  were discarded before anything was committed and the runs repeated.
- **Mapping the scanners to more controls:** each mapping names only the slice the tool actually
  checked (see `## Honest edges`); `comp-ai` maps to none.

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
