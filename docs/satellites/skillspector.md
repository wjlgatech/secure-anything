# Satellite digest — `skillspector`

> **Status: 🟡 digested → 🟢 integrated (2026-11-26).** Facts below were read from the upstream
> README **at the pinned SHA** and from the installed tool's own `--help` on 2026-11-26. Nothing
> is recalled; anything not read is labelled `UNCONFIRMED`. Pointer + digest — **never vendored**.

| field | value |
|---|---|
| upstream | https://github.com/NVIDIA/SkillSpector |
| pinned_sha | `c323ad4c43e3c8f2de051572cc25b2711d11e648` (release v2.13.7 — the PyPI version installed here) |
| license | Apache-2.0 |
| stars | 27,815 (GitHub API, 2026-11-26) |
| upstream last push | 2026-11-25 |
| verified_at | 2026-11-26 |
| role | scanner (agent-skill supply chain) |
| covers | LLM01, LLM03, ASI04 *(our mapping, not the upstream project's claim)* |

## What it is (verbatim from the README at the pin)

> **Security scanner for AI agent skills.** Detect vulnerabilities, malicious patterns, and
> security risks before installing agent skills.

> SkillSpector helps you answer: **"Is this skill safe to install?"**

Two stages: fast static analysis (patterns, YARA, AST/taint) plus an optional LLM semantic pass.
`--no-llm` runs the static stage only — no provider key, no network.

## How it is invoked here

```bash
pipx install --python python3.13 skillspector        # README: Python 3.12/3.13 for YARA wheels
skillspector scan <skill-dir>/ --no-llm --format json --output <out>.json
```

Run with every provider key unset, over `~/.claude/skills` (Paul's own skills only).

## Receipts (runs/skillspector/)

A recursive scan of the folder stopped at an aggregate report limit after 17 skills (coverage
28.3%, reported by the tool itself), so each skill was then scanned on its own: **108 of 110
scanned** (2 are symlinks it refuses to follow), 6 CRITICAL, 4 HIGH, 8 MEDIUM, 90 LOW. Every
CRITICAL/HIGH was read by hand; besides the three below, the rest (`gstack`, `living-repo`,
`moomooapi`, `install-moomoo-opend`, `synced`, …) are cleanup `rm -f`, an API key sent to its own
provider, `os.environ.copy()` for a subprocess, and an anti-injection rule that quotes the attack. Triage of the HIGH/CRITICAL hits read by hand:

- `dreammaketrue` CRITICAL "env → network": the env var is `DMT_API_URL`, the *destination*,
  not a credential — false positive.
- `copilotkit` HIGH "credential access": a printed hint mentioning `.env.local` — false positive.
- `freellmapi` HIGH "external script fetching / chaining": the skill tells the agent to run
  `curl … | bash` with a third-party install script — **real, low**: it offers a pinned
  alternative on the next line; the pipe-to-shell line should go.

## Honest edges

- Static-only here; the LLM stage (the semantic half) was not run.
- Its own report is honest about partial coverage — a skill it did not reach is not "clean".
