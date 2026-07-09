# 03 — Architecture

## Data flow

```
GitHub ──webhook──▶ FastAPI (/webhooks/github)
                       │  1. verify HMAC-SHA256 signature   (reject 401 if bad)
                       │  2. parse pull_request event
                       │  3. classify actor (human|ai_agent|bot)
                       │  4. enqueue job  ──────────────┐
                       └── 202 queued                    │
                                                         ▼
                                                     Queue (memory dev / Redis prod)
                                                         │
                                                         ▼
Worker  ──▶ fetch changeset (GitHub API)
        ──▶ run deterministic checks  (secret_scan · touched_paths · diff_size)
        ──▶ optional LLM risk review  (or "no evidence => escalate")
        ──▶ decision  (actor-aware policy)
        ──▶ append to hash-chained audit ledger  (Postgres)
        ──▶ persist PRReview  (idempotent on delivery_id)
        ──▶ post check-run + review back to GitHub
```

## Why webhook and worker are split

The webhook returns in milliseconds (verify → enqueue → 202). Heavy work (API fetch,
checks, LLM) runs in a separate worker. Under a burst of 50 agents opening PRs at once,
the API never blocks; workers drain the queue. Dev uses an in-process queue; prod uses
Redis so API and workers are separate processes/containers (see `docker-compose.yml`).

## Modules (`src/agentgate/`)

| Module | Responsibility |
|---|---|
| `config.py` | Env-loaded settings (secrets never logged) |
| `domain.py` | Pure runtime types: `Actor`, `ChangeSet`, `CheckResult`, `Decision`, enums |
| `actor.py` | Classify author → human / ai_agent / bot |
| `webhooks/github.py` | HMAC verification + event parsing |
| `checks/` | Deterministic evidence collectors (+ `paths.py` glob matcher, `registry.py`) |
| `policy/` | `schema.py` (pydantic), `default_policy.yaml`, `engine.py` (loader) |
| `review/llm_review.py` | Optional LLM risk-review seam |
| `decision.py` | Actor-aware gate logic (block / auto-approve / escalate) |
| `audit.py` | Hash-chained, tamper-evident ledger + `verify_chain` |
| `models.py` / `db.py` | ORM (`AuditEvent`, `PRReview`) + engine/session |
| `queue.py` | In-memory / Redis job queue |
| `github_client.py` | Fetch PR files, post decision (no-op when unauthenticated) |
| `worker.py` | `evaluate()` pure core + `process_job()` + `run()` loop |
| `main.py` | FastAPI: webhook, `/healthz`, `/reviews/recent`, `/audit/verify` |

## Key design choices

- **Policy as data, outside the prompt.** A jailbroken agent can't argue past a YAML file.
- **Pure core, I/O at the edges.** `evaluate()` and `decide()` are pure → fully unit-tested
  offline; GitHub/LLM live behind seams and are faked in tests.
- **Idempotency on `delivery_id`.** GitHub redelivers webhooks; we process each once.
- **Honest failure.** Missing LLM evidence on a risky diff escalates; a hard block (secret)
  requests changes. Stubs raise `NotImplementedError`, never fake success.

## Scale target

10–50 coding agents × daily PRs = low hundreds of jobs/day — trivial for a single worker.
Architecture (stateless API, queue, horizontal workers, Postgres) scales to thousands/day
by adding workers. Bottleneck at high volume is the GitHub API + LLM latency, both per-job
and parallelizable.
