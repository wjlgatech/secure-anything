# Contributing — for humans **and** AI agents

This repo is built to be worked on by a mix of human developers and AI coding agents. It also
eats its own dog food: the AgentGate organ is the kind of gate that should eventually review PRs
*to this very repo*.

## The one rule that matters

**`make check` must pass before any PR.** It is the canonical gate, CI runs exactly it, and
`anyagent goal --drive` discovers it. An honest ❌ beats a fake ✅: **never weaken a test to make
it green.** If a budget or a gate blocks you, cut real work or raise it in a PR with a reason —
do not edit the threshold in passing.

```bash
make install
make check     # ruff · charter manifest · registry evidence · build drift · self-audit · pytest
```

What each stage means:

| stage | fails when |
|---|---|
| `lint` | ruff finds an issue in `src`, `tests` or `scripts` |
| `manifest` | a charter doc is missing, too short, or lost a required heading |
| `registry` | a status claims evidence that isn't on disk (no digest, no pinned SHA, no receipt) |
| `build-check` | a generated surface (README blocks, the flagship SKILL.md) drifted from `data/` |
| `ainative` | a discipline regressed — the self-audit dropped below 90 |
| `test` | any test fails, including the architectural invariants |

## This is a meta-repo — know which layer you are in

| layer | where | rule |
|---|---|---|
| **core** | `src/secure_anything/*.py` | ≤600 LOC total · imports no organ · names no vendor or protocol. Enforced by `tests/test_core_invariants.py`. |
| **organs** | `src/secure_anything/organs/<name>/` | domain logic lives HERE. May import the core; the core may never import back. |
| **satellites** | `data/registry.yml` + `docs/satellites/<id>.md` | pointer + pinned SHA + digest. **Never vendored, never forked.** |
| **spec** | `data/*.yml` | the single source of truth. Published surfaces are generated from it. |

**If you are about to add a feature to the core, stop.** Add an organ, or a satellite entry.
A meta-repo that grows domain logic has failed at its only job.

## Ground rules for AI agents specifically

- **Small, single-purpose PRs.** Large diffs and touching protected paths (`**/policy/**`,
  `data/**`, `**/ledger.py`, `**/signing.py`, `.github/workflows/**`, `**/auth/**`, migrations,
  Dockerfiles) will be escalated to a human by the gate — that's expected, not a failure.
- **Never hardcode secrets** in code or tests. The secret scanner hard-blocks the PR.
- **Policy is data, not prompt.** Behaviour changes go in `default_policy.yaml` (versioned,
  reviewed), never buried in code or a system prompt.
- **Never hand-edit a generated block.** Change `data/`, then run `make build`. A generated file
  edited directly is a build failure, not a style preference.
- **Keep the gate deterministic and offline.** No network, no API key in `make check`. External
  calls live behind seams and are faked in tests. A capability that needs a credential is
  reported `NOT_MEASURED` — never silently passed.
- **No silent stubs.** If something isn't implemented, raise `NotImplementedError` with a note.
- **Verify, never recall.** Any external fact entering `data/` (a star count, a licence, a SHA,
  an arXiv id, a paper title) is read from the API or the primary source and stamped with
  `verified_at`. If you couldn't read it, tier it `claimed` or `disputed` and say so — do not
  round a memory up to a fact.
- **Respect the evidence ladder.** Never restate a `claimed` number as a fact, and never promote
  a capability without its on-disk receipt. The validator will refuse you anyway.

## Where things live

Read [README.md](README.md), then [docs/VISION.md](docs/VISION.md) for the charter and
[docs/META_REPO_PLAYBOOK.md](docs/META_REPO_PLAYBOOK.md) for the doctrine.

- **Adding a capability?** One entry in `data/registry.yml` (⚪), then a digest in
  `docs/satellites/<id>.md` with a pinned SHA (🟡), then a run receipt in `runs/<id>/` (🟢).
  If it costs more than that, the composition layer has leaked domain logic.
- **Adding a knowledge card?** `data/knowledge.yml`, with an evidence tier and a `verified_at`.
- **Adding a routing claim?** `eval/secure-anything.md` — it is parsed into pytest cases, so an
  unroutable claim fails the build.
- **Adding a check to the AgentGate organ?** `src/secure_anything/organs/agentgate/checks/`,
  register in `checks/registry.py`, add a deterministic test. See
  [docs/organs/agentgate/README.md](docs/organs/agentgate/README.md).
- **Every consequential behaviour appends to the audit ledger** (`secure_anything.ledger`).
