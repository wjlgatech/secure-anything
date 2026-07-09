# AgentGate

**The trust & accountability gate for human + AI-agent code changes.**
First wedge: a **PR firewall for coding agents** — designed for a world where 10–50
developers *and* AI coding agents open pull requests every day.

> When agents stop *talking* and start *doing* (merging code, moving money, mutating
> prod), the question is no longer "did it say something wrong?" It's **"is this actor
> allowed to take *this action*, and can we prove it later?"** AgentGate is the gate
> that answers it — for humans and AI agents alike.

---

## What it does

Every pull request — whether authored by a human or an AI coding agent — passes through
a policy gate before it can merge:

```
human devs ─┐
            ├──PR──▶ [ AGENTGATE ] ──▶ protected branch
AI agents ──┘            │
                         ├─ classify actor (human | ai_agent | bot)
                         ├─ deterministic checks (secrets · protected paths · diff size)
                         ├─ optional LLM risk review
                         ├─ policy-as-data decision (actor-aware)
                         │     • auto-approve the safe ones
                         │     • request changes on hard blocks (e.g. a secret)
                         │     • escalate risky ones to a human approver
                         └─ immutable, hash-chained audit trail
```

**Actor-aware by design ("for human + AI agents"):** AI agents are held to a stricter
bar than humans by default — an agent only auto-merges *low*-risk PRs; anything riskier
routes to a human. All configurable in [`default_policy.yaml`](src/agentgate/policy/default_policy.yaml).

## Why this exists

The full origin story — how a hands-on build on Juji led to a market read, to the "next
choke point," to this product — lives in **[docs/00-BACKGROUND.md](docs/00-BACKGROUND.md)**.
The competitive landscape and demand signals are in **[docs/01-MARKET.md](docs/01-MARKET.md)**;
the plan (with a SPEC per stage) is in **[ROADMAP.md](ROADMAP.md)**.

## Quickstart

```bash
make install            # pip install -e ".[dev]"
make check              # ruff + pytest  (this is the canonical gate)
make run                # uvicorn on :8099
# or the full stack (api + worker + postgres + redis):
cp .env.example .env    # set GITHUB_WEBHOOK_SECRET
make docker-up
```

Point a GitHub App's webhook at `POST /webhooks/github` (see [docs/03-ARCHITECTURE.md](docs/03-ARCHITECTURE.md)).

## Status (honest)

- ✅ Core pipeline built + **25 tests pass, lint clean**: webhook HMAC verification,
  actor classification, deterministic checks, actor-aware decision engine, tamper-evident
  audit ledger, idempotent job processing.
- ✅ Live-verified: unsigned webhook → `401`; signed PR event → `202 queued`.
- 🚧 **Stubbed / next:** live GitHub check-run + review posting, the LLM reviewer's
  Anthropic call, Redis worker in prod, GitHub App token minting. Seams are in place
  (`github_client.py`, `review/llm_review.py`) with honest `NotImplementedError`s, not
  fake passes.

## Layout

```
src/agentgate/        core service (see docs/03-ARCHITECTURE.md)
  webhooks/           GitHub webhook verify + parse
  checks/             deterministic evidence collectors
  policy/             policy-as-data (schema + default_policy.yaml + loader)
  review/             optional LLM risk-review seam
  decision.py         actor-aware gate logic
  audit.py            hash-chained ledger
  worker.py           evaluate → audit → persist → post
  main.py             FastAPI app
tests/                25 offline, deterministic tests
docs/                 background story · market · roadmap · architecture · security · policy
```

Private and proprietary — see [LICENSE](LICENSE). Contributor guide (human + AI):
[AGENTS.md](AGENTS.md).
