# Satellite digest — `gitleaks`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/gitleaks/gitleaks |
| pinned_sha | `83d9cd684c87d95d656c1458ef04895a7f1cbd8e` (release v8.30.1 — the binary run here, sha256 checked) |
| license | MIT |
| stars | 31,376 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-25 |
| verified_at | 2026-11-26 |
| role | scanner (secrets) |
| covers | LLM02 *(our mapping, not the upstream project's claim)* |

## What it is (from the README at the pin)

A regex + entropy secret scanner for git history, directories and stdin. Relevant features read
at the pin: `--redact` ("redact secrets from logs and stdout"), a per-finding **Fingerprint**,
and a `.gitleaksignore` file of fingerprints for triaged findings ("this feature is experimental
and is subject to change"). Default exit code when leaks are found: 1 (`--exit-code`).

## How it is invoked here

```bash
gitleaks git <bare-mirror> --log-opts=--all --redact --no-banner \
  --report-format json --report-path <out>.json [--gitleaks-ignore-path <repo>/.gitleaksignore]
```

## Receipts (runs/gitleaks/)

| target | before triage | after (.gitleaksignore with a reason per line) |
|---|---|---|
| agentic-portfolio | exit 1 — 10 hits (8 generic-api-key, 2 linkedin-client-id) | exit 0 |
| ContentFactory | exit 1 — 1 hit (generic-api-key) | exit 0 |
| secure-anything | exit 0 — 0 hits | — |

All 11 were false positives, read by hand: a .env-parser test fixture, prose ("$10/mo in API
credits"), a reCAPTCHA *site* key (public by design) in a scraped form, a function name
(`linkedinActivityTimeMs`), and a fake `AIzaSyTEST-…` key in a test. Every suppression carries
its reason in the repo's `.gitleaksignore`.

## Honest edges

- Pattern-only: no verification, so it over-reports (11 vs TruffleHog's 0). That is why it is the
  second opinion, not the gate.
- Not on the 12-tool list; added because the brief allowed "TruffleHog (or gitleaks)".
