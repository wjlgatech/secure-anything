"""The human-approval loop: authorization + audit, with a recording fake GitHub."""
from __future__ import annotations

from secure_anything.ledger import AuditLedger
from secure_anything.organs.agentgate.approvals import can_approve, process_approval
from secure_anything.organs.agentgate.config import Settings
from secure_anything.organs.agentgate.domain import ApprovalCommand
from secure_anything.store import AuditEvent


def test_can_approve_only_write_and_above():
    assert can_approve("admin") and can_approve("maintain") and can_approve("write")
    assert not can_approve("triage")
    assert not can_approve("read")
    assert not can_approve("none")


class _FakeGitHub:
    def __init__(self, permission: str):
        self._permission = permission
        self.approved: list = []
        self.refused: list = []

    def permission_level(self, repo, login):
        return self._permission

    def head_sha(self, repo, number):
        return "sha-head"

    def approve(self, repo, number, sha, approver, *, audit_id=""):
        self.approved.append((repo, number, sha, approver, audit_id))

    def refuse_approval(self, repo, number, commenter, level):
        self.refused.append((repo, number, commenter, level))


def _cmd(commenter="carol") -> ApprovalCommand:
    return ApprovalCommand(repo="octo/repo", number=7, commenter=commenter, delivery_id="d9")


def test_write_access_approves_and_audits(session):
    gh = _FakeGitHub("write")
    granted = process_approval(_cmd(), session=session, settings=Settings(_env_file=None),
                               github=gh)
    assert granted is True
    assert gh.approved and gh.approved[0][3] == "carol"
    assert gh.refused == []

    events = session.query(AuditEvent).all()
    assert [e.kind for e in events] == ["pr_approval"]
    assert events[0].payload["granted"] is True
    assert events[0].payload["permission"] == "write"
    assert AuditLedger(session).verify() is True
    # the on-chain audit id is what the approval comment references
    assert gh.approved[0][4] == events[0].hash


def test_no_write_access_is_refused_and_audited(session):
    gh = _FakeGitHub("read")
    granted = process_approval(_cmd("mallory"), session=session,
                               settings=Settings(_env_file=None), github=gh)
    assert granted is False
    assert gh.approved == []
    assert gh.refused and gh.refused[0][2] == "mallory"

    events = session.query(AuditEvent).all()
    assert [e.kind for e in events] == ["pr_approval_denied"]
    assert events[0].payload["granted"] is False
    assert AuditLedger(session).verify() is True
