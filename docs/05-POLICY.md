# 05 — Policy specification

Policy is the single source of truth for the gate. It is **data** (`default_policy.yaml`),
versioned and reviewed — not logic buried in code or a prompt. The editing path itself is a
protected path, so changing policy routes to a human.

## Schema (`policy/schema.py`)

```yaml
version: "0.1"

# Author login/app-slug containing any of these => treated as an AI coding agent.
agent_identities: [claude, cursor, devin, copilot, codex, aider, sweep, ...]

checks:
  diff_size:
    max_churn: 800        # added+deleted lines above this => MEDIUM risk
    hard_max_churn: 3000  # above this => HIGH risk
  secret_scan:
    enabled: true         # a hit is a HARD BLOCK (request changes)
  touched_paths:
    severity: high        # risk tier if a protected path is touched
    protected: ["<glob>", ...]

# Per-actor gating. "for human + AI agents": agents get a stricter bar.
actors:
  human:     { max_auto_approve_risk: medium, require_human_on: [high] }
  ai_agent:  { max_auto_approve_risk: low,    require_human_on: [medium, high] }
  bot:       { max_auto_approve_risk: low,    require_human_on: [high] }
```

## Decision semantics (`decision.py`), in order

1. **Any failed *blocking* check** (e.g. a secret in the diff) → `request_changes`.
2. **Overall risk** = max severity across failed checks and the LLM review.
3. **No evidence ⇒ escalate:** if an LLM review was expected but unavailable and risk ≥
   MEDIUM → `escalate_to_human` (never auto-approve on missing evidence).
4. Risk tier ∈ actor's `require_human_on` → `escalate_to_human`.
5. Else risk ≤ actor's `max_auto_approve_risk` → `auto_approve`.
6. Else → `escalate_to_human`.

## Risk tiers

- **low** — routine change within limits, no protected paths, no secrets.
- **medium** — larger diff than `max_churn`, or LLM-flagged moderate concern.
- **high** — protected path touched, diff over `hard_max_churn`, or a detected secret.

## Worked examples

| Author | Change | Risk | Action |
|---|---|---|---|
| human | 15-line src edit | low | auto_approve |
| human | 900-line refactor | medium | auto_approve (human bar) |
| ai_agent | 900-line refactor | medium | **escalate** (agent bar) |
| ai_agent | edits `.github/workflows/ci.yml` | high | **escalate** |
| anyone | diff contains `AKIA…` secret | high | **request_changes** (hard block) |

## Extending

Add a check in `checks/`, register it in `checks/registry.py`, expose its config in
`policy/schema.py`, and add a test. Keep it deterministic and offline.
