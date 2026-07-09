"""GitHub webhook verification + parsing.

Signature verification is the first security gate: every request must carry a valid
HMAC-SHA256 over the raw body using the shared secret. Reject anything else.
"""
from __future__ import annotations

import hashlib
import hmac

from ..actor import classify_actor
from ..domain import PullRequest
from ..policy.schema import Policy

# PR actions worth (re)evaluating.
REVIEWABLE_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}


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
