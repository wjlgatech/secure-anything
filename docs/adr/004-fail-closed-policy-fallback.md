# ADR-004 — A missing policy document must fail CLOSED

- **Status:** Accepted
- **Date:** 2026-08-03
- **Supersedes/relates to:** [ADR-002](002-fail-closed-and-separation-of-duties.md)

## Context

`load_policy(path)` returned a bare `Policy()` when the document was missing, with a comment
claiming this was "the strictest built-in defaults (every risk tier requires a human)".

**The comment was false.** A bare `Policy()` has `touched_paths.protected == []`, so no path is
protected; every check therefore passes, risk resolves to LOW, and an AI-agent PR — including one
touching `.github/workflows/**` — **auto-approves**.

This was found on 2026-08-03 while moving AgentGate under the organ seam. Three call sites had
hardcoded the policy location as the string `"src/agentgate/policy/default_policy.yaml"`. The move
invalidated all three, `load_policy` silently fell back, and four tests failed with
`AUTO_APPROVE` where they expected `ESCALATE`.

Two failures, not one:

1. **A fail-open fallback** in a product whose entire thesis is fail-closed gating.
2. **A comment asserting a safety property the code did not have** — the most dangerous kind of
   documentation, because it stops people checking.

The tests caught it. Nothing else would have.

## Decision

1. `load_policy` falls back to **`Policy.strict()`** — an explicit deny-by-default posture where
   every actor kind routes every risk tier (`low`, `medium`, `high`) to a human. A missing policy
   now blocks merges instead of waving them through.
2. The default policy path is resolved from `__file__`
   (`policy.DEFAULT_POLICY_PATH`), never from a CWD-relative string. A directory move cannot
   silently swap in a different policy again.
3. `tests/test_policy_fail_closed.py` pins all of it, including a test that **documents the trap**
   (`test_bare_policy_is_fail_open_which_is_why_strict_exists`) rather than trusting a comment.

## Consequences

- **Positive:** the failure mode of a misconfigured deployment is now "nothing merges" rather than
  "everything merges". That is the correct direction for a firewall.
- **Positive:** the path bug class is eliminated, not just fixed once.
- **Negative:** a deployment with a genuinely missing policy will block all merges until it is
  fixed. This is intended, and it is loud rather than silent — which is the whole point.
- **Rejected alternative:** raising `FileNotFoundError`. Fail-closed by exception is also correct,
  but it takes the whole service down rather than the merge, losing the audit trail of *why*
  things were blocked. A strict policy still runs the gate and still writes to the ledger.

## Lesson banked

A safety comment is a claim, and an unverified claim is exactly what this repo exists to refuse.
Assertions about behaviour belong in tests, not in prose above the code.
