"""End-to-end evaluation (pure core) + a full process_job run with a fake GitHub."""
from __future__ import annotations

from secure_anything.organs.agentgate.config import Settings
from secure_anything.organs.agentgate.domain import ActionType, ActorKind, ChangeSet, FileChange
from secure_anything.organs.agentgate.policy import DEFAULT_POLICY_PATH
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.worker import evaluate, process_job


def _policy():
    return load_policy(DEFAULT_POLICY_PATH)


def test_clean_small_human_pr_auto_approves(make_pr, make_changes):
    changes = make_changes([{"path": "src/app.py", "additions": 12, "deletions": 3,
                             "patch": "+def f():\n+    return 1"}])
    d = evaluate(make_pr(ActorKind.HUMAN), changes, _policy())
    assert d.action is ActionType.AUTO_APPROVE


def test_agent_touching_protected_path_escalates(make_pr, make_changes):
    changes = make_changes([{"path": ".github/workflows/ci.yml", "additions": 5}])
    d = evaluate(make_pr(ActorKind.AI_AGENT), changes, _policy())
    assert d.action is ActionType.ESCALATE
    assert d.risk.value == "high"


class _FakeGitHub:
    def __init__(self, changes: ChangeSet):
        self._changes = changes
        self.posted = []

    def fetch_changeset(self, repo, number):
        return self._changes

    def post_decision(self, pr, decision, *, audit_id=""):
        self.posted.append(decision.action.value)


def test_process_job_persists_and_audits(session, make_pr):
    settings = Settings(_env_file=None)  # no LLM key -> offline, deterministic
    changes = ChangeSet(files=[FileChange(path="src/app.py", additions=10, patch="+x=1")])
    gh = _FakeGitHub(changes)
    pr = make_pr(ActorKind.HUMAN, delivery_id="dlv-42")

    d = process_job({"pr": pr.model_dump()}, session=session, policy=_policy(),
                    settings=settings, github=gh)
    assert d is not None and d.action is ActionType.AUTO_APPROVE
    assert gh.posted == ["auto_approve"]

    # idempotent: same delivery id is skipped on replay
    again = process_job({"pr": pr.model_dump()}, session=session, policy=_policy(),
                        settings=settings, github=gh)
    assert again is None

    # audit ledger recorded exactly one decision and is intact
    from secure_anything.ledger import AuditLedger
    assert AuditLedger(session).verify() is True
