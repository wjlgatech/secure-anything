# Satellite digest — `codex-security`

> **Status: 🟡 digested.** Facts below were read from the upstream repo **at the pinned SHA** on
> 2026-08-03. Nothing here is recalled from memory; anything not directly read is labelled
> `UNCONFIRMED`. This is a pointer + digest — the repo is **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/openai/codex-security |
| pinned_sha | `0572feb293e4ec49956fde99b4d6843a80ea884b` |
| license | Apache-2.0 (SPDX resolved by the GitHub API) |
| stars | 8,332 |
| upstream last push | 2026-08-03 |
| verified_at | 2026-08-03 |
| role | scanner |
| covers | LLM02, LLM03, LLM05, ASI05 *(our mapping, not OpenAI's claim)* |

## What it is (verbatim from the upstream README at the pin)

> `@openai/codex-security` is a CLI and TypeScript SDK for finding, validating, and fixing
> security vulnerabilities in your code.

## How it is invoked (read from the README, not invented)

```bash
npm install @openai/codex-security
npx @openai/codex-security login
npx @openai/codex-security scan .
npx @openai/codex-security scan . --mode deep --workers 2 --subagents 0 \
    --stop-after-no-new 3 --max-discovery-runs 10
```

- **Requirements:** Node.js ≥22.13.0 (22.x line), 24.x or 26.x; Python ≥3.10; access to Codex Security.
- **CI auth:** set `OPENAI_API_KEY` or `CODEX_API_KEY` instead of interactive sign-in. The README
  states environment API keys are passed to the current scan and "never stored in Codex's
  credential home or system keyring".
- **Credential precedence:** interactive scans prompt when both a ChatGPT sign-in and an API key
  exist; non-interactive scans keep API-key precedence. `--auth chatgpt|api-key` selects explicitly.
- **State:** scan history lives in the workbench state directory; `CODEX_SECURITY_STATE_DIR`
  relocates it outside the repository.
- **Diffing:** `scans compare BEFORE_SCAN_ID AFTER_SCAN_ID` matches findings by root cause and
  classifies them new / persisting / reopened / resolved / unknown. Notably honest upstream
  behaviour: **missing findings stay `unknown` when coverage was incomplete** rather than being
  reported as resolved — the same no-evidence-means-no discipline this repo gates on.
- **TypeScript SDK:** `new CodexSecurity()` → `await security.run(".", {...})` → `result.reportPath`.
- **Containers:** an official image plus Docker Compose config for non-interactive, resumable bulk
  scans pinned to immutable Git revisions.

## Why it is in the registry

The scanner Paul named, and the strongest available example of the *validate-before-reporting*
pattern: candidate vulnerabilities are executed in a sandbox to kill false positives before a human
sees them. That is the same seam shape as AgentGate's checks — evidence first, verdict second.

## Integration notes (why it is 🟡 and not 🟢)

1. **It cannot run inside `make check`.** It requires a credential and network. Under our gate it is
   therefore a `NOT_MEASURED` capability, reported by name — never a silent pass.
2. **Promotion path to 🟢:** invoke it through the core gate seam against a fixture repo, capture
   `exit_code` + the report path into `runs/codex-security/`, then flip status. Until that receipt
   exists, `scripts/verify_registry.py` refuses the promotion.
3. **Licence:** Apache-2.0 confirmed, so integration is permitted. Still a pointer — we invoke the
   published npm package, we do not fork it.

## UNCONFIRMED / do not repeat as fact

- The widely reported figures (1.2M commits scanned; 792 critical + 10,561 high-severity issues
  found in open source; 16 of 23 seeded vulnerabilities caught ≈ 70%) are **vendor-reported via
  secondary press coverage**. Not independently verified, no error bars, seeded set not public.
  Tracked as an explicitly `claimed` knowledge card (`claimed-codex-security-catch-rate`) so that
  when we run it here at M2 we can compare measured behaviour against what was claimed.
- Reported command-injection flaw in a branch-name parameter (disclosed 2025-12-16, patched
  2026-02-05) comes from secondary coverage; not verified against upstream commit history.
