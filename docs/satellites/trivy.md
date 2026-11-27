# Satellite digest — `trivy`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/aquasecurity/trivy |
| pinned_sha | `3f6334d223b52188324af3b9923b4249cd206652` (release v0.76.2 — the binary run here, sha256 checked) |
| license | Apache-2.0 |
| stars | 39,803 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-26 |
| verified_at | 2026-11-26 |
| role | scanner (dependencies / supply chain) |
| covers | LLM03, ASI04 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> Trivy is a comprehensive and versatile security scanner. Trivy has *scanners* that look for
> security issues, and *targets* where it can find those issues.

Targets include container images, filesystems, remote git repositories, VM images and Kubernetes;
scanners include SBOM, known vulnerabilities (CVEs), IaC misconfigurations, secrets and licences.

## How it is invoked here

```bash
trivy fs --scanners vuln --quiet --skip-dirs node_modules --severity HIGH,CRITICAL \
  --exit-code 1 --format json -o <out>.json <checkout>
```

## Receipts (runs/trivy/)

| target | before | after |
|---|---|---|
| agentic-portfolio | exit 1 — 4 CRITICAL, 44 HIGH | exit 1 — 0 CRITICAL, 4 HIGH (CopilotKit 1.5 / openai 4 chains, held by a ceiling) |
| ContentFactory | exit 0 — 0 | exit 0 — 0 |

## Honest edges

- **Trivy skips npm dev dependencies unless `--include-dev-deps`** (read from `--help`). It
  reported ContentFactory clean while npm audit and osv-scanner both saw 5 high advisories in the
  dev-only wrangler toolchain. Run it with a second engine, or pass the flag.
- Counts are per installed package version, not per advisory, so they do not equal npm audit's.
- Downloads its vulnerability DB on first run (network).
