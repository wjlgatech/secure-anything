"""Parsing the `/agentgate approve` comment command out of an issue_comment event."""
from __future__ import annotations

from secure_anything.organs.agentgate.webhooks.github import parse_issue_comment_event


def _event(body: str, *, action: str = "created", is_pr: bool = True) -> dict:
    issue: dict = {"number": 7}
    if is_pr:
        issue["pull_request"] = {"url": "https://api.github.com/repos/octo/repo/pulls/7"}
    return {
        "action": action,
        "repository": {"full_name": "octo/repo"},
        "issue": issue,
        "comment": {"body": body, "user": {"login": "carol"}},
    }


def test_parses_approve_command():
    cmd = parse_issue_comment_event(_event("please /agentgate approve now"), delivery_id="d1")
    assert cmd is not None
    assert cmd.repo == "octo/repo" and cmd.number == 7
    assert cmd.commenter == "carol" and cmd.delivery_id == "d1"


def test_command_is_case_insensitive():
    assert parse_issue_comment_event(_event("/AgentGate Approve")) is not None


def test_ignores_comment_without_command():
    assert parse_issue_comment_event(_event("looks good to me 👍")) is None


def test_ignores_non_pr_issue():
    assert parse_issue_comment_event(_event("/agentgate approve", is_pr=False)) is None


def test_ignores_edited_or_deleted_comments():
    assert parse_issue_comment_event(_event("/agentgate approve", action="edited")) is None
