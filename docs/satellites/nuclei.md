# Satellite digest — `nuclei`

> **Status: 🟡 digested — ran, but did NOT measure the app (2026-11-26); not promoted.** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/projectdiscovery/nuclei |
| pinned_sha | `a8c88feb4a1c8e961b7902534ce3af97e9d524a4` (release v3.11.1 — the binary run here, sha256 checked; templates v10.5.2) |
| license | MIT |
| stars | 33,340 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-26 |
| verified_at | 2026-11-26 |
| role | scanner (live target / DAST-lite) |
| covers | LLM02 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> Nuclei is a modern, high-performance vulnerability scanner that leverages simple YAML-based
> templates.

## How it is invoked here — safe mode only, own systems only

```bash
nuclei -u https://<own-site> -tags exposure,misconfig,takeover \
  -etags intrusive,dos,fuzz,fuzzing,bruteforce,brute-force,rce,sqli -dast=false \
  -no-interactsh -rl 2 -c 2 -bs 2 -timeout 10 -jsonl -o <out>.jsonl -store-resp -srd <dir>
```

2,069 templates / 4,899 requests. No fuzzing, no intrusive or DoS templates, no out-of-band
callbacks (`-no-interactsh`), low rate limit (`-rl`, default 150 per `--help`).

## Receipts (runs/nuclei/)

Receipt (critical-severity safe templates, 1 req/s, `-ms` so every response is kept): **79
results, 0 matches — and 73 of the 79 responses were Vercel's 403 challenge, the other 6 had no
HTTP response. Zero reached the app**, so a "clean" result would be a lie; the capability stays 🟡.

First pass, earlier the same night, not receipt-captured (2,069 templates, 5 req/s): 10 matches, all
`http-missing-security-headers` (info) — **matched on a Vercel "Security Checkpoint" 403
challenge page**, not on the site. The live site does send CSP, HSTS, nosniff, referrer and
permissions policies (checked with curl). The firewall challenging an unknown scanner is itself
a working control; it also means a clean Nuclei result is only as good as the share of requests
that reached the app.

## Honest edges

- Behind a bot-mitigating edge (Vercel, Cloudflare) an external scan measures the edge first. To
  measure the app, scan a preview deployment with the firewall bypass for your own IP.
- Active scanner: never point it at a system you do not own.
