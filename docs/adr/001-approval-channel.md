# ADR 001 — Human approval via PR comment command

- **Status:** accepted
- **Date:** 2026-07-09
- **Deciders:** Paul Wu (solo + coding agents)

## Context
Phase 1 ([`docs/specs/phase-1-github-loop.md`](../specs/phase-1-github-loop.md)) needs a
way for a human to approve an **escalated** PR — the moment that turns "the gate blocked
this" into "a named, authorized human unblocked it, and we can prove it." The channel must
verify **authorization** (does this person have write access?), not merely identity, and it
must land in the tamper-evident audit ledger. The SPEC lists two options.

## Options considered
1. **PR comment command (`/agentgate approve`)** — the approver comments on the PR; we
   consume the `issue_comment` webhook, verify their repo permission via the GitHub API,
   record it, and flip the check to success.
   - **Pros:** zero new UI; approval lives next to the discussion; fastest path to the
     "catch-it-live" demo; reuses the webhook + queue we already have.
   - **Cons:** anyone can *type* the command → authorization check is load-bearing (a comment
     is only an identity *claim*); command must be parsed robustly.
2. **Minimal signed web action** — a small authenticated web view with an "Approve" button.
   - **Pros:** an explicit, harder-to-spoof surface; room for richer context.
   - **Cons:** new auth story (sessions/OAuth), new surface to secure and host, slower to
     demo — scope that belongs in Phase 4 (multi-tenant), not Phase 1.

## Decision
**Comment command (`/agentgate approve`).** It is the fastest credible path to the Phase 1
demo and reuses the existing signed-webhook + queue + ledger machinery. The security bar is
met not by the channel but by an explicit **authorization check**: we call
`GET /repos/{repo}/collaborators/{login}/permission` and only honor `admin | maintain |
write` (see `github_client.APPROVE_PERMISSIONS` / `approvals.can_approve`). Both the grant
and any refusal are appended to the audit ledger.

## Consequences
- **Easier:** no new auth surface; the approval flows through the same verified webhook as
  everything else; the demo is a single comment.
- **Harder / to watch:** the authorization check is now security-critical — a bug there is a
  privilege-escalation bug, so it is unit-tested directly (`test_approvals.py`) and the
  denial path is audited, not silent.
- **Revisit in Phase 4:** a signed web action (option 2) may return for multi-tenant use,
  where per-org RBAC and a richer approver experience matter; this ADR would then be
  superseded, not reversed.
