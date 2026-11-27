# Satellite digest — `claude-code-security-review`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/anthropics/claude-code-security-review |
| pinned_sha | `0c6a49f1fa56a1d472575da86a94dbc1edb78eda` (main at 2026-11-26 — the commit the family repos' CI pins) |
| license | MIT |
| stars | 7,141 (GitHub API, 2026-11-26) |
| upstream last push | 2026-02-11 |
| verified_at | 2026-11-26 |
| role | scanner (AI diff review) |
| covers | LLM02, LLM05 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> An AI-powered security review GitHub Action using Claude to analyze code changes for security
> vulnerabilities.

Features read at the pin: diff-aware scanning (PRs: changed files only), PR comments, false-
positive filtering, custom scan/filter instructions. Inputs: `claude-api-key` (required),
`comment-pr`, `exclude-directories`, `claudecode-timeout` (default 20), `claude-model`,
`run-every-commit` (default false — it reviews a PR once and skips later pushes via a cache key).

## How it is invoked here

In the family repos' `.github/workflows/security.yml` as job `ai-review`: pinned by SHA,
`continue-on-error: true` (advisory, never blocking), skipped for bot-authored PRs (each run
spends API credit), and a NOT-MEASURED notice when the `ANTHROPIC_API_KEY` secret is absent.

## Receipts (runs/claude-code-security-review/)

agentic-portfolio PR #594 (commit 1039980): `files_reviewed: 12`, `review_completed: true`,
**0 findings**, action exit 0 — run 45929841327 on GitHub Actions (observed remotely; the
results artifact is pinned by sha256 in the receipt). The rebased head (809f493) was skipped by
the action's once-per-PR cache, as designed.

## Honest edges

- README: "This action is not hardened against prompt injection attacks and should only be used
  to review trusted PRs." Both family repos are private, so every PR author is a collaborator.
- Needs a paid key; ContentFactory has none yet, so there it reports NOT MEASURED.
- 0 findings on one PR is one sample, not a catch rate.
