# Satellite digest — `trufflehog`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/trufflesecurity/trufflehog |
| pinned_sha | `4ef51f69ca6347aaa76a5e64a87eac9c0c909f71` (release v3.100.1 — the binary run here, sha256 checked against the release checksums) |
| license | AGPL-3.0 (SPDX resolved by the GitHub API) |
| stars | 29,718 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-25 |
| verified_at | 2026-11-26 |
| role | scanner (secrets) |
| covers | LLM02 *(our mapping, not the upstream project's claim)* |

## What it is (from the README at the pin)

> TruffleHog is the most powerful secrets **Discovery, Classification, Validation,** and
> **Analysis** tool. In this context, secret refers to a credential a machine uses to
> authenticate itself to another machine.

Its distinguishing move is **verification**: for each candidate credential it calls the issuing
provider, so a result is labelled verified / unverified / unknown ("verification failed due to
error", per `--help`) rather than "looks like a key".

## How it is invoked here

```bash
trufflehog git file://<bare-mirror> --bare --json --no-update \
  --results=verified,unknown,unverified --fail      # --fail: exit 183 if any result
```

- Full history over **every ref** of a `git clone --mirror` (branches, tags, PR heads).
  `file://` on a bare mirror needs `--bare` (without it the scan errors on a missing `.git`).
- CI (family repos): `trufflesecurity/trufflehog@<v3.100.1 sha>` on each PR's commits with
  `--results=verified,unknown` — fails on a live or un-rule-out-able credential only.

## Receipts (runs/trufflehog/)

2026-11-26: agentic-portfolio (all refs), ContentFactory (all refs), secure-anything (all refs):
**0 results of any class**, exit 0 each. Cross-checked by `gitleaks` (11 hits, all false
positives — see its digest): two engines, one verdict.

## Honest edges

- Verification needs network to each provider; an offline run reports unverified results only.
- AGPL-3.0: run the released binary as a subprocess; never link or vendor.
- LLM02 here means the *credentials-in-source* slice of sensitive-information disclosure — not
  an LLM leaking data at runtime.
