#!/usr/bin/env python3
"""AgentGate "caught in the act" demo — the shareable red-light moment.

Runs the REAL gate pipeline (the same `evaluate()` + hash-chained `AuditLedger` used in
production) fully offline, against five scenarios an AI coding agent might attempt:

  1. a clean, small human PR            -> auto-approved   (the gate isn't just "no")
  2. an agent smuggling an AWS secret    -> hard-blocked
  3. an agent rewriting CI               -> escalated to a human
  4. an agent landing a 4,000-line diff  -> escalated to a human
  5. an agent editing its OWN policy     -> escalated (the gate protects itself)

Then it prints the tamper-evident ledger and proves it detects tampering.

No network, no key, no GitHub App. Run it:  python scripts/demo_bypass_caught.py
(from the repo root, with `make install` done). Exit code is non-zero if any decision
deviates from the expected outcome — so this doubles as an end-to-end smoke test.
"""
from __future__ import annotations

import sys

from sqlalchemy.orm import sessionmaker

from secure_anything.ledger import AuditLedger
from secure_anything.organs.agentgate.db import init_db, make_engine
from secure_anything.organs.agentgate.domain import (
    Actor,
    ActorKind,
    ActionType,
    ChangeSet,
    FileChange,
    PullRequest,
)
from secure_anything.store import AuditEvent
from secure_anything.organs.agentgate.policy import DEFAULT_POLICY_PATH
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate

GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)
LIGHT = {
    ActionType.AUTO_APPROVE: f"{GREEN}🟢 AUTO-APPROVE{RESET}",
    ActionType.REQUEST_CHANGES: f"{RED}🔴 REQUEST CHANGES (hard block){RESET}",
    ActionType.ESCALATE: f"{YELLOW}🟠 ESCALATE → human{RESET}",
}


def _pr(kind: ActorKind, login: str, title: str) -> PullRequest:
    return PullRequest(repo="acme/payments", number=1, title=title,
                       actor=Actor(login=login, kind=kind, label=login))


# (label, PR, changeset, expected action) — each scenario drives the real evaluate().
SCENARIOS = [
    (
        "Human dev — small, clean bug fix",
        _pr(ActorKind.HUMAN, "alice", "fix: off-by-one in pagination"),
        ChangeSet(files=[FileChange(path="src/pager.py", additions=8, deletions=3,
                                    patch="+    return items[start:end]")]),
        ActionType.AUTO_APPROVE,
    ),
    (
        "AI agent — smuggles an AWS secret into the diff",
        _pr(ActorKind.AI_AGENT, "claude-code[bot]", "chore: add config"),
        ChangeSet(files=[FileChange(path="src/config.py", additions=2,
                                    patch='+AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')]),
        ActionType.REQUEST_CHANGES,
    ),
    (
        "AI agent — rewrites the CI pipeline",
        _pr(ActorKind.AI_AGENT, "devin-ai", "ci: 'optimize' the workflow"),
        ChangeSet(files=[FileChange(path=".github/workflows/ci.yml", additions=20,
                                    deletions=15, patch="+      - run: echo skip tests")]),
        ActionType.ESCALATE,
    ),
    (
        "AI agent — lands a 4,000-line diff",
        _pr(ActorKind.AI_AGENT, "cursor-agent", "refactor: everything"),
        ChangeSet(files=[FileChange(path="src/monolith.py", additions=4000, patch="+# ...")]),
        ActionType.ESCALATE,
    ),
    (
        "AI agent — edits its OWN guardrails (the bypass move)",
        _pr(ActorKind.AI_AGENT, "sweep-ai", "chore: tidy policy"),
        ChangeSet(files=[FileChange(
            path="src/secure_anything/organs/agentgate/policy/default_policy.yaml", additions=3,
            patch="+  ai_agent: { max_auto_approve_risk: high }")]),
        ActionType.ESCALATE,
    ),
]


def main() -> int:
    policy = load_policy(DEFAULT_POLICY_PATH)
    engine = make_engine("sqlite:///:memory:")
    init_db(engine)
    Session = sessionmaker(bind=engine, future=True, expire_on_commit=False)

    print(f"\n{BOLD}🛡️  AgentGate — caught in the act{RESET}")
    print(f"{DIM}Same pipeline as production: evaluate() + hash-chained audit. "
          f"No network, no key.{RESET}\n")

    failures = 0
    with Session() as session:
        ledger = AuditLedger(session)
        for label, pr, changes, expected in SCENARIOS:
            decision = evaluate(pr, changes, policy)
            ok = decision.action is expected
            failures += not ok
            mark = f"{GREEN}✓{RESET}" if ok else f"{RED}✗ EXPECTED {expected.value}{RESET}"

            print(f"{BOLD}{label}{RESET}")
            print(f"   author: {pr.actor.kind.value:9}  risk: {decision.risk.value:6}  "
                  f"→ {LIGHT[decision.action]}  {mark}")
            for reason in decision.reasons:
                print(f"   {DIM}• {reason}{RESET}")
            ledger.append("pr_decision", {
                "repo": pr.repo, "title": pr.title, "actor": pr.actor.kind.value,
                "action": decision.action.value, "risk": decision.risk.value,
            })
            print()

        # The audit trail: tamper-evident by construction.
        print(f"{BOLD}📜 Audit ledger (hash-chained){RESET}")
        events = session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
        for e in events:
            print(f"   {DIM}#{e.id} {e.kind} {e.hash[:12]}…  prev {e.prev_hash[:12]}…{RESET}")
        print(f"   verify → {GREEN if ledger.verify() else RED}intact: {ledger.verify()}{RESET}")

        # Prove it actually detects tampering (not just a claim).
        first = session.query(AuditEvent).order_by(AuditEvent.id.asc()).first()
        # rewrite history to a value that differs from what was recorded
        first.payload = {**first.payload, "action": "secretly_approved"}
        session.commit()
        intact_after = ledger.verify()
        detected = intact_after is False
        failures += not detected
        print(f"   {DIM}tamper test: edited decision #{first.id} → "
              f"verify now {intact_after} "
              f"({'✓ tamper detected' if detected else '✗ NOT detected'}){RESET}\n")

    if failures:
        print(f"{RED}{BOLD}DEMO FAILED: {failures} outcome(s) deviated from expected.{RESET}\n")
        return 1
    print(f"{GREEN}{BOLD}All scenarios behaved as policy dictates. "
          f"Red light, screenshot, share.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
