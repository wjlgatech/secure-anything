# Satellite digest — `osv-scanner`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/google/osv-scanner |
| pinned_sha | `02f96a40691c2d155fdda799af436e111231e365` (release v2.7.1 — the binary run here) |
| license | Apache-2.0 |
| stars | 11,643 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-26 |
| verified_at | 2026-11-26 |
| role | scanner (dependencies / supply chain) |
| covers | LLM03, ASI04 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> Use OSV-Scanner to find existing vulnerabilities affecting your project's dependencies.

It is the officially supported front end to the OSV.dev database and a CLI over OSV-Scalibr.
Data sent to the API "includes package names, versions, ecosystems, and file hashes"; `--offline`
disables network requests against a local database.

## How it is invoked here

```bash
osv-scanner scan source -r --format json --output-file <out>.json <checkout>   # exit 1 = any vuln
```

## Receipts (runs/osv-scanner/)

| target | before | after |
|---|---|---|
| agentic-portfolio | exit 1 — 36 vulnerable packages, 129 advisories | exit 1 — 15 packages, 34 advisories |
| ContentFactory | exit 1 — 5 packages, 30 advisories | **exit 0 — 0** |

## Honest edges

- All severities and dev dependencies count, so it is stricter than the family repos' CI gate
  (which blocks on production high/critical only).
- Not on the 12-tool list; run as the cross-check that caught Trivy's dev-dependency blind spot.
