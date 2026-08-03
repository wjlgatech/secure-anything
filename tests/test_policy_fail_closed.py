"""A missing policy document must FAIL CLOSED (ADR-002, ADR-004).

Regression test for a real fail-open found on 2026-08-03: three call sites hardcoded the
policy path as a string, the organ move invalidated them, and `load_policy` fell back to a
bare `Policy()` — which protects nothing, so an AI-agent PR touching a protected path
AUTO-APPROVED. The fallback is now `Policy.strict()`.
"""
from secure_anything.organs.agentgate.domain import ActionType, ActorKind, ChangeSet, FileChange
from secure_anything.organs.agentgate.policy import DEFAULT_POLICY_PATH
from secure_anything.organs.agentgate.policy.engine import load_policy
from secure_anything.organs.agentgate.policy.schema import Policy
from secure_anything.organs.agentgate.worker import evaluate


def test_default_policy_path_actually_exists():
    """The path is resolved from __file__, so a directory move can never silently
    swap in a permissive policy again."""
    assert DEFAULT_POLICY_PATH.exists(), DEFAULT_POLICY_PATH


def test_missing_policy_file_falls_back_to_strict_not_bare():
    p = load_policy("does/not/exist.yaml")
    for kind in ("human", "ai_agent", "bot"):
        ap = p.actor_policy(kind)
        assert set(ap.require_human_on) == {"low", "medium", "high"}, kind


def test_bare_policy_is_fail_open_which_is_why_strict_exists():
    """Documents the trap rather than trusting a comment: a bare Policy() auto-approves."""
    changes = ChangeSet(files=[FileChange(path=".github/workflows/ci.yml", additions=5)])
    pr = _agent_pr()
    assert evaluate(pr, changes, Policy()).action is ActionType.AUTO_APPROVE
    assert evaluate(pr, changes, Policy.strict()).action is not ActionType.AUTO_APPROVE


def test_missing_policy_blocks_an_agent_pr(make_pr):
    changes = ChangeSet(files=[FileChange(path=".github/workflows/ci.yml", additions=5)])
    d = evaluate(make_pr(ActorKind.AI_AGENT), changes, load_policy("does/not/exist.yaml"))
    assert d.action is not ActionType.AUTO_APPROVE


def _agent_pr():
    from secure_anything.organs.agentgate.domain import Actor, PullRequest

    return PullRequest(
        repo="o/r", number=1,
        actor=Actor(login="claude-code[bot]", kind=ActorKind.AI_AGENT, label="claude-code"),
    )
