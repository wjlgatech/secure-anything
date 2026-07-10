# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

AgentGate is a **PR firewall for human + AI-agent code changes**: every pull request passes
through a policy gate (verify → classify actor → deterministic checks → optional LLM review →
actor-aware decision → hash-chained audit) before it can merge. The full product context is in
`ROADMAP.md` (single source of truth) and `docs/`; contributor rules are in `AGENTS.md`.

## Commands

```bash
make install   # pip install -e ".[dev]"  (Python >=3.11)
make check     # ruff check + pytest — THE canonical gate; CI runs exactly this
make test      # pytest only
make lint      # ruff check src tests
make fmt       # ruff format
make run       # uvicorn on :8099
make worker    # run the evaluation worker loop
make docker-up # full stack: api + worker + postgres + redis
```

Run a single test: `python -m pytest tests/test_decision.py::test_name -q`
(`pyproject.toml` sets `pythonpath = ["src"]`, so tests import `agentgate` without install.)

`make check` is the contract. Never weaken a test to make it pass — an honest ❌ beats a fake ✅.

## Architecture

The pipeline is split into an **I/O edge** and a **pure core** so the core is fully testable
offline (all 25 tests are deterministic, no network, no API key).

**Request flow:** `main.py` (FastAPI) receives `POST /webhooks/github` → `webhooks/github.py`
verifies the HMAC signature (401 on failure — the first security gate) and parses the event into
a `PullRequest`, classifying the author via `actor.py` → enqueues a job (`queue.py`) and returns
`202` fast. A separate `worker.py` loop dequeues and does the heavy work.

**Evaluation (`worker.py`):**
- `evaluate(pr, changes, policy, ...)` is the **pure, deterministic core** used by tests:
  runs every check → optional LLM review → `decide()`. No I/O.
- `process_job(...)` wires in the datastore + GitHub: idempotency guard (one decision per
  webhook `delivery_id`), fetch changeset, evaluate, append to audit ledger, persist, post back.

**Key modules:**
- `domain.py` — all core types (`PullRequest`, `ChangeSet`, `CheckResult`, `Decision`, and the
  `ActorKind`/`RiskTier`/`ActionType` enums). Pure data, no I/O. Start here.
- `checks/` — deterministic evidence collectors (`SecretScanCheck`, `TouchedPathsCheck`,
  `DiffSizeCheck`). Each subclasses `checks/base.Check` and is listed in `checks/registry.py`.
- `decision.py` — combines check results + LLM review into one `Decision`. The rule order is
  documented at the top of the file and is the heart of the gate's behaviour.
- `policy/` — **policy is DATA, not prompt**: `default_policy.yaml` is the single source of
  truth, loaded into the `Policy` pydantic model (`schema.py`) via `engine.py`.
- `audit.py` — tamper-evident, hash-chained ledger (`hash = sha256(prev|kind|canonical(payload))`).
- `github_client.py`, `review/llm_review.py` — external-call **seams**, faked in tests.

## Invariants (these govern behaviour — respect them)

- **Actor-aware gating.** AI agents are held to a stricter bar than humans. This lives entirely
  in `default_policy.yaml` (`actors:` — `max_auto_approve_risk`, `require_human_on`) and is
  enforced by `decide()`. Change gate behaviour there, not in code.
- **Policy is data, not prompt.** Behaviour changes go in the versioned/reviewed YAML, never
  buried in code or an LLM system prompt. A jailbroken agent can't argue past a YAML file.
- **No evidence ⇒ escalate.** If an LLM review was expected but unavailable and risk ≥ MEDIUM,
  `decide()` forces ESCALATE — never auto-approve on missing evidence.
- **Checks are deterministic and offline.** No network, no API key in checks or tests. All
  external calls live behind seams and are faked in tests.
- **No silent stubs.** Unimplemented paths raise `NotImplementedError` with a note (see
  `github_client.post_decision`), never fake a success.
- **Everything consequential appends to the audit ledger.** New gate outcomes / overrides must
  be recorded via `AuditLedger.append(...)`.

## Adding a check

Create it under `checks/`, subclass `Check`, register it in `checks/registry.default_checks()`,
add its config to `policy/schema.py` + `default_policy.yaml`, and add a deterministic test in
`tests/`. A failed check reports a `severity` (its risk IF failed) and `blocking` (if failed,
hard-block with `request_changes` rather than escalate).

## Current status

Phase 0 (offline core) is done. Phase 1 (live GitHub loop) is next — see `ROADMAP.md` and
`docs/specs/`. Stubbed/next: live GitHub check-run + review posting, the LLM reviewer's Anthropic
call, Redis worker in prod, GitHub App token minting. Seams exist; they raise, they don't lie.
