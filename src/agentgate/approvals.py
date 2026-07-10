"""The human-approval loop: a `/agentgate approve` comment on an escalated PR.

Authorization is the crux: identity (who commented) comes from the signed webhook,
but *permission* (may they approve?) is verified against GitHub's repo-permission API
at processing time — never trusted from the payload. Both the grant and the denial are
appended to the tamper-evident audit ledger, so "who unblocked this, and were they
allowed to?" is answerable after the fact.
"""
from __future__ import annotations

import logging

from .config import Settings
from .domain import ApprovalCommand
from .github_client import APPROVE_PERMISSIONS, GitHubClient

log = logging.getLogger("agentgate.approvals")


def can_approve(permission_level: str) -> bool:
    """True iff a repo permission level is allowed to approve an escalated PR."""
    return permission_level in APPROVE_PERMISSIONS


def process_approval(
    cmd: ApprovalCommand, *, session, settings: Settings, github: GitHubClient | None = None
) -> bool:
    """Verify the commenter's write access, record it to the ledger, and (if allowed)
    unblock the PR. Returns whether the approval was granted."""
    from .audit import AuditLedger

    gh = github or GitHubClient(settings)
    level = gh.permission_level(cmd.repo, cmd.commenter)
    allowed = can_approve(level)

    event = AuditLedger(session).append(
        "pr_approval" if allowed else "pr_approval_denied",
        {"repo": cmd.repo, "number": cmd.number, "delivery_id": cmd.delivery_id,
         "approver": cmd.commenter, "permission": level, "granted": allowed},
    )
    session.commit()

    if allowed:
        sha = gh.head_sha(cmd.repo, cmd.number)
        gh.approve(cmd.repo, cmd.number, sha, cmd.commenter, audit_id=event.hash)
        log.info("approval granted for %s#%s by %s", cmd.repo, cmd.number, cmd.commenter)
    else:
        gh.refuse_approval(cmd.repo, cmd.number, cmd.commenter, level)
        log.info("approval refused for %s#%s by %s (permission=%s)",
                 cmd.repo, cmd.number, cmd.commenter, level)
    return allowed
