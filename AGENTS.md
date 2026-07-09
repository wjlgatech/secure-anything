# Contributing — for humans **and** AI agents

This repo is built to be worked on by a mix of human developers and AI coding agents.
It also eats its own dog food: AgentGate is the kind of gate that should eventually
review PRs *to this very repo*.

## The one rule that matters

**`make check` must pass before any PR.** That's `ruff check` + `pytest`. It's the
canonical gate — CI runs exactly this, and it's what an `anyagent goal --drive` run will
discover. An honest ❌ beats a fake ✅: never weaken a test to make it green.

```bash
make install
make check
```

## Ground rules for AI agents specifically

- **Small, single-purpose PRs.** Large diffs and touching protected paths
  (`.github/workflows/**`, `**/auth/**`, `src/agentgate/policy/**`, migrations, Dockerfiles)
  will be escalated to a human by the gate — that's expected, not a failure.
- **Never hardcode secrets** in code or tests. The secret scanner will hard-block the PR.
- **Policy is data, not prompt.** Behaviour changes go in `default_policy.yaml` (versioned,
  reviewed), not buried in code or a system prompt.
- **Keep checks deterministic and offline.** Tests must not hit the network or require an
  API key. External calls live behind seams (`github_client.py`, `review/llm_review.py`)
  and are faked in tests.
- **No silent stubs.** If something isn't implemented, raise `NotImplementedError` with a
  note — do not fake a success path.

## Where things live

Read [docs/03-ARCHITECTURE.md](docs/03-ARCHITECTURE.md) first. Add a new check under
`src/agentgate/checks/`, register it in `checks/registry.py`, and add a test in
`tests/`. Every new consequential behaviour should append to the audit ledger.
