"""GitHub client request-building, tested fully offline via httpx.MockTransport.

No key, no network: we inject a client whose transport answers canned responses and
records what the client *sent*, so pagination, payload shapes, and the decision->
check-run/review mapping are all real code under test."""
from __future__ import annotations

import httpx
import pytest

from agentgate.config import Settings
from agentgate.domain import Actor, ActorKind, ActionType, Decision, PullRequest, RiskTier
from agentgate.github_client import GitHubClient


def _settings() -> Settings:
    return Settings(_env_file=None, GITHUB_API_BASE="https://api.github.com")


def _client(handler, sent: list):
    def _record(request: httpx.Request) -> httpx.Response:
        return handler(request, sent)

    transport = httpx.MockTransport(_record)
    gh = GitHubClient(
        _settings(),
        client=httpx.Client(transport=transport),
        token_provider=lambda: "test-token",
    )
    return gh


def _pr(**kw) -> PullRequest:
    base = dict(repo="octo/repo", number=7, actor=Actor(login="a", kind=ActorKind.HUMAN),
                head_sha="deadbeef")
    base.update(kw)
    return PullRequest(**base)


def test_fetch_changeset_follows_pagination():
    def handler(request, sent):
        sent.append(str(request.url))
        if request.url.params.get("page") == "2" or "page=2" in str(request.url):
            return httpx.Response(200, json=[{"filename": "b.py", "additions": 2}])
        # page 1 -> point to page 2 via a Link header
        return httpx.Response(
            200,
            json=[{"filename": "a.py", "additions": 1, "deletions": 1, "patch": "+x"}],
            headers={"Link": '<https://api.github.com/repos/octo/repo/pulls/7/files?page=2>; '
                             'rel="next"'},
        )

    sent: list = []
    gh = _client(handler, sent)
    changes = gh.fetch_changeset("octo/repo", 7)

    assert changes.paths == ["a.py", "b.py"]
    assert len(sent) == 2  # both pages fetched
    assert changes.files[0].churn == 2


def test_fetch_changeset_empty_without_token():
    gh = GitHubClient(_settings(), token_provider=lambda: "")
    assert gh.fetch_changeset("octo/repo", 7).files == []


def test_post_decision_escalate_blocks_merge():
    def handler(request, sent):
        sent.append((request.method, request.url.path, request.read()))
        return httpx.Response(201, json={"id": 1})

    sent: list = []
    gh = _client(handler, sent)
    decision = Decision(action=ActionType.ESCALATE, risk=RiskTier.HIGH,
                        reasons=["touched_paths: .github/workflows/ci.yml"])
    gh.post_decision(_pr(), decision, audit_id="hash123")

    paths = [p for _, p, _ in sent]
    assert paths == [
        "/repos/octo/repo/check-runs",
        "/repos/octo/repo/pulls/7/reviews",
        "/repos/octo/repo/issues/7/comments",
    ]
    check_body = sent[0][2].decode()
    # escalate must NOT be a passing check, so branch protection keeps merge blocked
    assert '"conclusion":"action_required"' in check_body
    review_body = sent[1][2].decode()
    assert '"event":"COMMENT"' in review_body
    assert "hash123" in sent[2][2].decode()


def test_post_decision_auto_approve_maps_to_success():
    def handler(request, sent):
        sent.append((request.url.path, request.read().decode()))
        return httpx.Response(201, json={"id": 1})

    sent: list = []
    gh = _client(handler, sent)
    gh.post_decision(_pr(), Decision(action=ActionType.AUTO_APPROVE, risk=RiskTier.LOW))

    assert '"conclusion":"success"' in sent[0][1]
    assert '"event":"APPROVE"' in sent[1][1]


def test_post_decision_noop_without_token():
    calls: list = []
    gh = GitHubClient(_settings(), client=httpx.Client(
        transport=httpx.MockTransport(lambda r: calls.append(r) or httpx.Response(200))),
        token_provider=lambda: "")
    gh.post_decision(_pr(), Decision(action=ActionType.AUTO_APPROVE, risk=RiskTier.LOW))
    assert calls == []  # nothing posted when unauthenticated


@pytest.mark.parametrize("level,expected", [("write", "write"), ("admin", "admin")])
def test_permission_level(level, expected):
    def handler(request, sent):
        return httpx.Response(200, json={"permission": level})

    gh = _client(handler, [])
    assert gh.permission_level("octo/repo", "alice") == expected


def test_permission_level_404_is_none():
    def handler(request, sent):
        return httpx.Response(404, json={})

    gh = _client(handler, [])
    assert gh.permission_level("octo/repo", "stranger") == "none"


def test_approve_flips_check_to_success():
    def handler(request, sent):
        sent.append((request.url.path, request.read().decode()))
        return httpx.Response(201, json={"id": 1})

    sent: list = []
    gh = _client(handler, sent)
    gh.approve("octo/repo", 7, "sha1", "maintainer", audit_id="h1")

    assert sent[0][0] == "/repos/octo/repo/check-runs"
    assert '"conclusion":"success"' in sent[0][1]
    assert sent[1][0] == "/repos/octo/repo/issues/7/comments"
    assert "maintainer" in sent[1][1]
