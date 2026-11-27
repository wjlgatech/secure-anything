# Satellite digest — `semgrep`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/semgrep/semgrep |
| pinned_sha | `082ca45478ee4dcc4275d805c0325a7fcd509990` (release v1.187.0 — the version run here (pipx)) |
| license | LGPL-2.1 |
| stars | 17,995 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-27 |
| verified_at | 2026-11-26 |
| role | scanner (static analysis) |
| covers | LLM02, LLM05, ASI05 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> Semgrep is a fast, open-source, static analysis tool that searches code, finds bugs, and
> enforces secure guardrails and coding standards.

> Semgrep analyzes code locally on your computer or in your build environment: **by default,
> code is never uploaded**.

## How it is invoked here

```bash
semgrep scan --metrics=off --config p/default --config p/javascript --config p/typescript \
  --config p/secrets --config p/nextjs --exclude node_modules --json -o <out>.json \
  --severity ERROR --error .           # the gate: exit 1 on any ERROR-severity finding
```

CI (family repos) adds `--baseline-commit <PR base sha>` so only findings a PR *introduces* fail.

## Receipts (runs/semgrep/)

- agentic-portfolio **before** (ab680f1): ERROR gate exit 1 — 2 findings: `run-shell-injection`
  (a `workflow_dispatch` input spliced into a bash `run:` — real, fixed in agentic-portfolio
  PR #594) and `react-insecure-request` (an `http://127.0.0.1` CDP probe — false positive,
  suppressed inline with its reason).
- agentic-portfolio **after** (043b03d): ERROR gate exit 0. All-severity run: 799 results,
  WARNING/INFO only (non-literal RegExp built from escaped constants, `<link rel=canonical>`
  flagged as missing SRI, mutable action tags in older workflows).
- ContentFactory (74e77fa): ERROR gate exit 0; 189 WARNING, 162 of them in never-deployed
  `reference-code/`. (One receipt shows exit 1: an all-severity run where `--error` was passed by
  mistake — kept, because receipts are append-only.)

## Honest edges

- The README itself says Community Edition "will miss many true positives as it can only analyze
  code within the boundaries of a single function or file". A clean ERROR gate is a floor.
- Registry rule packs are fetched over the network, so this is a sweep/CI capability, never part
  of the offline `make check`.
- LGPL-2.1: subprocess only, never link or vendor.
