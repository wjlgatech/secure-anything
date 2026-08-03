"""GitHub webhook verification + parsing.

Signature verification is the first security gate: every request must carry a valid
HMAC-SHA256 over the raw body using the shared secret. Reject anything else.
"""
from __future__ import annotations

import hashlib
import hmac

from ..actor import classify_actor
from ..domain import ApprovalCommand, PullRequest
from ..policy.schema import Policy

# PR actions worth (re)evaluating.
REVIEWABLE_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}

# The comment command a human uses to approve an escalated PR.
APPROVE_COMMAND = "/agentgate approve"


def verify_signature(secret: str, body: bytes, signature_header: str | None) -> bool:
    if not secret or not signature_header or not signature_header.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    expected = "sha256=" + digest
    # constant-time compare to avoid timing oracles
    return hmac.compare_digest(expected, signature_header)


def parse_pull_request_event(
    payload: dict, policy: Policy, delivery_id: str = ""
) -> PullRequest | None:
    if payload.get("action") not in REVIEWABLE_ACTIONS:
        return None
    pr = payload.get("pull_request") or {}
    repo = (payload.get("repository") or {}).get("full_name", "")
    user = pr.get("user") or {}
    actor = classify_actor(
        user.get("login", ""), user.get("type", "User"), policy.agent_identities
    )
    return PullRequest(
        repo=repo,
        number=int(pr.get("number", 0)),
        title=pr.get("title", "") or "",
        body=pr.get("body", "") or "",
        head_sha=(pr.get("head") or {}).get("sha", ""),
        actor=actor,
        delivery_id=delivery_id,
    )


def parse_issue_comment_event(payload: dict, delivery_id: str = "") -> ApprovalCommand | None:
    """Parse an `issue_comment` webhook into an ApprovalCommand, or None.

    Only newly-created comments *on a pull request* whose body carries the approve
    command qualify. Authorization is verified later, against GitHub — the payload's
    author is only an identity claim.
    """
    if payload.get("action") != "created":
        return None
    issue = payload.get("issue") or {}
    if "pull_request" not in issue:  # a comment on a plain issue, not a PR
        return None
    body = (payload.get("comment") or {}).get("body", "") or ""
    if APPROVE_COMMAND not in body.strip().lower():
        return None
    repo = (payload.get("repository") or {}).get("full_name", "")
    commenter = ((payload.get("comment") or {}).get("user") or {}).get("login", "")
    return ApprovalCommand(
        repo=repo, number=int(issue.get("number", 0)),
        commenter=commenter, delivery_id=delivery_id,
    )
