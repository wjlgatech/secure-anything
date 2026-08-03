"""FastAPI surface: the GitHub webhook entrypoint + health/audit endpoints.

The webhook verifies the signature, parses the PR event, and enqueues a job; a
separate worker does the heavy evaluation so the endpoint returns fast under load.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Header, HTTPException, Request
from sqlalchemy import select

from .config import get_settings
from .db import engine, init_db, session_factory
from .models import PRReview
from .policy.engine import load_policy
from .queue import get_queue
from .webhooks.github import (
    parse_issue_comment_event,
    parse_pull_request_event,
    verify_signature,
)

log = logging.getLogger("agentgate")

app = FastAPI(title="AgentGate", version="0.1.0")


@app.on_event("startup")
def _startup() -> None:
    init_db(engine())
    app.state.settings = get_settings()
    app.state.policy = load_policy(app.state.settings.policy_path)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok", "service": "agentgate"}


@app.post("/webhooks/github", status_code=202)
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    x_github_delivery: str | None = Header(default=None),
) -> dict:
    settings = getattr(app.state, "settings", None) or get_settings()
    policy = getattr(app.state, "policy", None) or load_policy(settings.policy_path)

    body = await request.body()
    if not verify_signature(settings.github_webhook_secret, body, x_hub_signature_256):
        # Reject unverified requests outright — the first security gate.
        raise HTTPException(status_code=401, detail="invalid signature")

    payload = await request.json()

    if x_github_event == "pull_request":
        pr = parse_pull_request_event(payload, policy, delivery_id=x_github_delivery or "")
        if pr is None:
            return {"status": "ignored", "action": payload.get("action")}
        get_queue(settings).enqueue({"kind": "pr_review", "pr": pr.model_dump()})
        return {"status": "queued", "repo": pr.repo, "number": pr.number,
                "actor_kind": pr.actor.kind.value}

    if x_github_event == "issue_comment":
        cmd = parse_issue_comment_event(payload, delivery_id=x_github_delivery or "")
        if cmd is None:
            return {"status": "ignored", "action": payload.get("action")}
        get_queue(settings).enqueue({"kind": "approval", "approval": cmd.model_dump()})
        return {"status": "queued", "kind": "approval",
                "repo": cmd.repo, "number": cmd.number}

    return {"status": "ignored", "event": x_github_event}


@app.get("/reviews/recent")
def recent_reviews(limit: int = 20) -> list[dict]:
    Session = session_factory()
    with Session() as s:
        rows = s.execute(
            select(PRReview).order_by(PRReview.id.desc()).limit(min(limit, 100))
        ).scalars().all()
        return [
            {"repo": r.repo, "number": r.number, "actor_login": r.actor_login,
             "actor_kind": r.actor_kind, "action": r.action, "risk": r.risk,
             "reasons": r.reasons, "created_at": r.created_at.isoformat()}
            for r in rows
        ]


@app.get("/audit/verify")
def audit_verify() -> dict:
    from ...ledger import AuditLedger

    Session = session_factory()
    with Session() as s:
        ledger = AuditLedger(s, signer=_audit_signer())
        return {"intact": ledger.verify(), "signed": _audit_signer() is not None}


def _audit_signer():
    """Load the Ed25519 audit signer from AGENTGATE_AUDIT_KEY (a PKCS8 PEM path), or
    None to run the unsigned hash-chain (ADR-003). Kept isolated so the pure ledger
    stays key-agnostic and offline-testable."""
    import os

    key_path = os.environ.get("AGENTGATE_AUDIT_KEY")
    if not key_path:
        return None
    from pathlib import Path

    from ...signing import Ed25519Signer

    return Ed25519Signer.load(Path(key_path))
