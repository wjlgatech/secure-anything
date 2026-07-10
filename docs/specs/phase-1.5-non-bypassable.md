# SPEC — Phase 1.5: Non-bypassable enforcement  (Status: 🎯 Next after P1)

## Goal
Make AgentGate the **only viable merge path**, protect the gate from the code it judges, and
base decisions on a **robust actor identity** — so the gate "100% finishes its mission" even
against a jailbroken or adversarial agent author. This closes the gap between "we post a
check" and "the check cannot be bypassed, disabled, or spoofed."

## Why (the load-bearing threat)
GitHub branch protection is **bypassable via GitHub Actions** — a write-capable actor can use
the workflow `GITHUB_TOKEN` to approve/merge its own PR (the `github-actions` bot is a
*different* identity), and a three-identity collusion (author, pusher, approver) defeats
"author ≠ approver." GitHub calls this "expected behavior" (Mercari, 2024), so **we must
mitigate it explicitly**. A firewall that ignores this is theater. Related: our current
`actor.py` classifies authors by login **substring** — spoofable — and our audit chain is only
tamper-evident *to us* (addressed in Phase 2 anchoring).

## User stories
- As a platform owner, an agent **cannot** merge to a protected branch by any path — not via a
  workflow token, a colluding second identity, or by disabling a check.
- As a security reviewer, I get a **report of every open bypass** on a repo before I trust it.
- As a compliance owner, an agent **cannot weaken its own guardrails** (policy / gate code)
  without a named human owner's approval.
- As an operator, if the gate is **down or errors**, merges are **blocked**, never waved
  through.

## In scope
1. **Hardened GitHub ruleset (config-as-code) + a verifier.** Ship the recommended ruleset and
   an `agentgate audit-repo` command that inspects a repo and reports each gap as a finding:
   - required AgentGate status check present;
   - "Allow GitHub Actions to create and approve pull requests" **disabled**;
   - "Require approval of the most recent reviewable push" **enabled**;
   - merge queue enabled (checks re-run against the real post-merge tree);
   - CODEOWNERS covers `src/agentgate/policy/**`, the gate's own code, `.github/workflows/**`;
   - bypass lists scoped so no bot can force-push/delete the protected branch.
2. **Fail-closed availability.** The required check reports `pending`/`failure` (blocks merge)
   whenever the gate is down, errored, or unreachable — never `success` on error. Run ≥2
   worker replicas so fail-closed ≠ permanent lockout; add an **audited** break-glass.
3. **Separation of duties / no self-approval.** An agent-authored PR requires an *additional*
   human approver; the approver's identity must differ from the PR author and every commit
   pusher. (`/agentgate approve` already verifies write access — extend to "not the author.")
4. **Robust actor identity.** Replace login-substring classification with **GitHub App
   attribution** (and, where available, OIDC/workload-identity) so an agent can't spoof a
   human login (or vice-versa).
5. **Protect the gate's own integrity.** SHA-pin all GitHub Actions (tags are mutable);
   `cosign`-sign the gate artifact and verify the signature at deploy; keep the policy file and
   gate code behind CODEOWNERS.

## Out of scope
External audit anchoring (WORM / timestamp / transparency log) → Phase 2. Multi-tenant RBAC → Phase 4.

## Design notes / decisions (→ ADRs)
- **Fail-closed vs fail-open** and **separation-of-duties** → [ADR-002](../adr/002-fail-closed-and-separation-of-duties.md) (accepted: fail-closed).
- Actor identity source (App attribution vs OIDC federation) — record an ADR when we build it;
  App attribution is the pragmatic first step, OIDC the stronger end state.
- The verifier is an `EvidenceCollector`-style read-only check (no evidence ⇒ report the gap);
  it never *changes* a repo's settings, it reports — a human applies the ruleset.

## Task checklist
- [ ] Ruleset template (JSON) + `agentgate audit-repo <owner/repo>` verifier w/ per-gap findings.
- [ ] Fail-closed path: on evaluator error/timeout, post a blocking (non-`success`) check; test it.
- [ ] Approval: reject `/agentgate approve` when approver == author or a commit pusher; audit the refusal.
- [ ] Actor identity via GitHub App attribution; deprecate login-substring (keep as fallback + warn).
- [ ] SHA-pin actions; cosign sign+verify the gate image; CODEOWNERS committed for policy + gate.
- [ ] Offline tests: mis-configured-repo fixture → verifier reports every gap; evaluator-raises → blocking verdict; self-approval → refused.

## Definition of Done
A **runnable check**: against a deliberately mis-configured repo fixture, `agentgate audit-repo`
reports each of the five bypass gaps; a test proves that when `evaluate()` raises, the gate
posts a **non-`success`** (merge-blocking) verdict; and a test proves `/agentgate approve` by
the PR's own author is **refused and audited**. All offline/deterministic; `make check` green.

## Risks / open questions
- GitHub may change ruleset semantics; pin to documented rules and re-test on API changes.
- Break-glass is a real bypass by design — it must be rare, time-boxed, and loudly audited.
- App-attribution edge cases (PRs opened by a human *running* an agent locally vs the agent's
  own App) — classification policy needs a decision (record it).
