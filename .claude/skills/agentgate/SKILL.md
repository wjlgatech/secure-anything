---
name: agentgate
description: >
  Master tool for AgentGate — the PR firewall for human + AI-agent code changes.
  Gate a change through the real pipeline offline, classify actors, change gate
  behaviour via policy YAML, verify the tamper-evident audit ledger, drive the live
  webhook service, add a new check. Trigger: /agentgate, "gate this PR", "run the
  firewall demo", "verify the audit ledger", "change the gate policy", "add a check".
---

# /agentgate — master tool for the PR firewall

Every example below runs the **real production pipeline** (`evaluate()` + hash-chained
`AuditLedger`), fully offline — no GitHub App, no network, no API key. All snippets are
verified against the codebase; run them from the repo root with the repo venv
(`.venv/bin/python`, created by `make install`).

**Ground rules (from `CLAUDE.md` — never violate):**
- **Policy is data, not prompt** — gate behaviour changes go in `src/secure_anything/organs/agentgate/policy/default_policy.yaml`, never in code or an LLM prompt.
- **No evidence ⇒ escalate** — never auto-approve on missing evidence.
- **`make check` is the contract** — never weaken a test to make it pass.

## 0. Setup (once)

```bash
make install        # pip install -e ".[dev]"  (Python >=3.11)
make check          # ruff + pytest — must be green before and after any change
```

---

## 1. Flagship demo — "caught in the act" ▶️

One command, five scenarios, tamper-proof proof. Exit code is non-zero if any
decision deviates, so it doubles as an end-to-end smoke test.

```bash
.venv/bin/python scripts/demo_bypass_caught.py
```

| # | Actor & attempt | Outcome |
|---|---|---|
| 1 | Human — small clean bug fix | 🟢 auto-approve |
| 2 | AI agent — smuggles an AWS secret | 🔴 request changes (hard block) |
| 3 | AI agent — rewrites CI | 🟠 escalate → human |
| 4 | AI agent — 4,000-line diff | 🟠 escalate → human |
| 5 | AI agent — **edits its own policy file** | 🟠 escalate (the gate protects itself) |

Then it prints the hash-chained ledger, verifies `intact: True`, and tampers with a
record to prove `verify → False`. Full narrative: `docs/DEMO.md`.

---

## 2. Gate any change offline (the pure core)

`evaluate(pr, changes, policy)` is deterministic given its inputs — same code path
production uses.

**2.1 Human, small clean fix → `auto_approve`**

```bash
.venv/bin/python - <<'EOF'
from secure_anything.organs.agentgate.domain import Actor, ActorKind, ChangeSet, FileChange, PullRequest
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate

policy = load_policy("src/secure_anything/organs/agentgate/policy/default_policy.yaml")
d = evaluate(
    PullRequest(repo="acme/api", number=42, title="fix: off-by-one",
                actor=Actor(login="alice", kind=ActorKind.HUMAN)),
    ChangeSet(files=[FileChange(path="src/pager.py", additions=8, deletions=3)]),
    policy)
print(d.action.value, d.risk.value)   # -> auto_approve low
EOF
```

**2.2 AI agent smuggles an AWS key → `request_changes` (hard block)**

```bash
.venv/bin/python - <<'EOF'
from secure_anything.organs.agentgate.domain import Actor, ActorKind, ChangeSet, FileChange, PullRequest
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate

policy = load_policy("src/secure_anything/organs/agentgate/policy/default_policy.yaml")
d = evaluate(
    PullRequest(repo="acme/api", number=43, title="chore: add config",
                actor=Actor(login="claude-code[bot]", kind=ActorKind.AI_AGENT)),
    ChangeSet(files=[FileChange(path="src/config.py", additions=2,
                                patch='+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')]),
    policy)
print(d.action.value, d.reasons)
# -> request_changes ['secret_scan: possible secret(s) in diff: aws_access_key']
EOF
```

**2.3 AI agent rewrites CI → `escalate_to_human` (protected path + strict agent bar)**

```bash
.venv/bin/python - <<'EOF'
from secure_anything.organs.agentgate.domain import Actor, ActorKind, ChangeSet, FileChange, PullRequest
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate

policy = load_policy("src/secure_anything/organs/agentgate/policy/default_policy.yaml")
d = evaluate(
    PullRequest(repo="acme/api", number=44, title="ci: optimize workflow",
                actor=Actor(login="devin-ai", kind=ActorKind.AI_AGENT)),
    ChangeSet(files=[FileChange(path=".github/workflows/ci.yml",
                                additions=20, deletions=15)]),
    policy)
print(d.action.value, d.risk.value)   # -> escalate_to_human high
EOF
```

---

## 3. Classify an actor (human / AI agent / bot)

Actor kind decides which policy bar applies (`actors:` in the YAML). The
`agent_identities` list in the policy is what marks a login as an AI agent.

```bash
.venv/bin/python - <<'EOF'
from secure_anything.organs.agentgate.actor import classify_actor
from secure_anything.organs.agentgate.policy.engine import load_policy

agents = load_policy("src/secure_anything/organs/agentgate/policy/default_policy.yaml").agent_identities
print(classify_actor("claude-code[bot]", "Bot", agents).kind.value)  # ai_agent
print(classify_actor("dependabot[bot]", "Bot", agents).kind.value)   # bot
print(classify_actor("alice", "User", agents).kind.value)            # human
EOF
```

---

## 4. Change gate behaviour — edit the YAML, never the code

`src/secure_anything/organs/agentgate/policy/default_policy.yaml` is the single source of truth. Three
common edits:

**4.1 Protect a new path** — add under `checks.touched_paths.protected`:

```yaml
      - "payments/**"
```

Verified effect (same agent PR flips from auto-approve to escalate):

```bash
.venv/bin/python - <<'EOF'
import tempfile, yaml
from secure_anything.organs.agentgate.domain import Actor, ActorKind, ChangeSet, FileChange, PullRequest
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate

data = yaml.safe_load(open("src/secure_anything/organs/agentgate/policy/default_policy.yaml"))
data["checks"]["touched_paths"]["protected"].append("payments/**")
with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
    yaml.safe_dump(data, f); edited = f.name

pr = PullRequest(repo="acme/api", number=7, title="feat: rounding",
                 actor=Actor(login="cursor-agent", kind=ActorKind.AI_AGENT))
ch = ChangeSet(files=[FileChange(path="payments/charge.py", additions=5)])
print("stock :", evaluate(pr, ch, load_policy("src/secure_anything/organs/agentgate/policy/default_policy.yaml")).action.value)  # auto_approve
print("edited:", evaluate(pr, ch, load_policy(edited)).action.value)                                      # escalate_to_human
EOF
```

**4.2 Recognize a new AI agent** — add its slug to `agent_identities:` (e.g. `- windsurf`).
Any author whose login contains it is then held to the `ai_agent` bar.

**4.3 Tighten or loosen a bar** — under `actors:`, e.g. force humans to review *every*
agent PR: set `ai_agent: {max_auto_approve_risk: low, require_human_on: [low, medium, high]}`.
Diff-size thresholds live under `checks.diff_size` (`max_churn`, `hard_max_churn`).

After any policy edit: `make check`, and note the change is versioned + reviewed —
a jailbroken agent can't argue past a YAML file.

---

## 5. Audit ledger — tamper-evident evidence

Every consequential event is hash-chained: `hash = sha256(prev | kind | canonical(payload))`.

**5.1 Append + verify, then prove tamper detection**

```bash
.venv/bin/python - <<'EOF'
from sqlalchemy.orm import sessionmaker
from secure_anything.ledger import AuditLedger
from secure_anything.organs.agentgate.db import init_db, make_engine
from secure_anything.store import AuditEvent

engine = make_engine("sqlite:///:memory:")
init_db(engine)
Session = sessionmaker(bind=engine, future=True, expire_on_commit=False)
with Session() as s:
    ledger = AuditLedger(s)
    ledger.append("pr_decision", {"repo": "acme/api", "action": "escalate_to_human"})
    ledger.append("human_approval", {"repo": "acme/api", "approver": "alice"})
    print("intact:", ledger.verify())                       # True
    row = s.query(AuditEvent).first()
    row.payload = {**row.payload, "action": "auto_approve"} # rewrite history
    s.commit()
    print("after tamper:", ledger.verify())                 # False — caught
EOF
```

**5.2 Verify the live service's ledger**

```bash
curl -s localhost:8099/audit/verify    # -> {"intact": true}
```

---

## 6. Run the live service (webhook loop)

**6.1 API + health**

```bash
make run                               # uvicorn on :8099
curl -s localhost:8099/healthz         # -> {"status":"ok","service":"agentgate"}
```

**6.2 The first security gate — unsigned webhooks are rejected**

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8099/webhooks/github -d '{}'
# -> 401 (invalid HMAC signature)
```

**6.3 Full stack + recent decisions**

```bash
make docker-up                         # api + worker + postgres + redis
curl -s localhost:8099/reviews/recent  # last gate decisions with actor/risk/reasons
```

Live GitHub wiring (App creds, `/agentgate approve` comment loop) is Phase 1 —
see `docs/DEMO.md` §3 and `docs/specs/phase-1-github-loop.md`.

---

## 7. Add a new check (recipe)

1. Create it under `src/secure_anything/organs/agentgate/checks/`, subclass `checks/base.Check`.
2. Register it in `checks/registry.default_checks()`.
3. Add its config to `policy/schema.py` **and** `default_policy.yaml`.
4. Add a deterministic test in `tests/` (no network, no key).
5. A failed check reports `severity` (its risk IF failed) and `blocking`
   (hard-block vs escalate).
6. `make check` must be green.

---

## 8. Report honestly

Relay decisions and check outcomes verbatim (`auto_approve` / `request_changes` /
`escalate_to_human`, risk tier, reasons). If `make check` fails, show the failure —
an honest ❌ beats a fake ✅.
