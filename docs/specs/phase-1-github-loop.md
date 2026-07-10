# SPEC — Phase 1: Live GitHub Loop  (Status: 🎯 Next)

## Goal
Make the gate act on a **real** repository: post its decision to GitHub, block merges when
needed, and give a human a real way to approve an escalated PR — producing the
"catch-it-in-the-act" demo.

## User stories
- As a maintainer, an agent's risky PR is **blocked** with a clear reason and a link to the
  audit record; a safe PR is auto-approved.
- As an approver, I can approve an escalated PR and my identity + timestamp are recorded.
- As a founder, I can screen-record an agent PR being caught, routed, and logged.

## In scope
1. **GitHub App**: mint short-lived installation tokens from the App private key.
2. **Post decisions**: create a **check-run** (blocks merge when not `auto_approve`) + a PR
   **review** (approve / request-changes) + a comment with reasons + audit id.
3. **Live changeset fetch** (`GET /pulls/{n}/files`), pagination, handle `synchronize` re-runs.
4. **Redis queue + worker** as separate processes (compose already wires this).
5. **Human approval loop**: an "approve" affordance (PR comment command `/agentgate approve`
   or a minimal signed web action) that records approver + timestamp to the ledger and
   flips the check to success.

## Out of scope
LLM reviewer (P2), non-GitHub actions (P3), multi-tenant auth (P4).

## Design notes / decisions to make (→ ADRs)
- Token minting: JWT from App key → installation token (cache per-installation, ~10 min TTL).
- Approval channel: comment-command vs. web view — pick one (ADR). Comment-command is
  fastest to demo; must verify the commenter has write access (authorization, not just auth).
- Merge-blocking: rely on branch protection "require check to pass" + our check-run.

## Task checklist
- [x] `github_client`: JWT → installation token (behind optional `[github]` extra); real
  `fetch_changeset` w/ pagination (Link-header cursor; fixed a params-override infinite loop).
- [x] `github_client.post_decision`: check-run + review + comment (replaced `NotImplementedError`).
  Escalate/request-changes map to non-`success` conclusions so branch protection blocks merge.
- [x] Approval command handler + write-access authorization check + ledger record
  (`approvals.py`, `webhooks.parse_issue_comment_event`, worker `handle_job` dispatch).
- [x] Offline integration tests via `httpx.MockTransport` (request-building, pagination,
  payload shapes, authorization, ledger) — 42 tests, deterministic, no network.
- [ ] Redis worker path verified end-to-end (compose up; PR → decision **on real GitHub**). ⏳ needs creds
- [ ] Demo script + recording: secret / CI-rewrite / 4k-diff each caught. ⏳ needs a live test repo

> **Honest status:** all code paths are built and covered by deterministic offline tests
> (the app boots; unsigned webhook → `401`, signed `/agentgate approve` → `202 queued`,
> `/audit/verify` → `intact`). What is **not** yet verified is the loop against a *real*
> GitHub App + repo (token minting, live check-run posting) — that requires credentials and
> a sandbox repo, and is the remaining gate for the Definition of Done below.

## Definition of Done
On a live test repo: an agent PR that touches a protected path is **escalated** (merge
blocked) and, after `/agentgate approve` by a write-access user, unblocks — with both the
decision and the approval in the audit ledger, and `GET /audit/verify` → `intact: true`.

## Risks / open questions
- GitHub API rate limits under burst → backoff + per-installation token cache.
- Approval authorization: must check the approver's repo permission, not just identity.
- Test strategy for live API without flakiness (fixtures vs. a sandbox org).
