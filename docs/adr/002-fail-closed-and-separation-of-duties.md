# ADR 002 — Fail-closed enforcement + separation of duties

- **Status:** accepted
- **Date:** 2026-07-10
- **Deciders:** Paul Wu (solo + coding agents)

## Context
AgentGate's core promise is that the gate is the *only* merge path and "100% finishes its
mission" even against an adversarial author. Two design questions decide whether that promise
holds ([SPEC: phase-1.5](../specs/phase-1.5-non-bypassable.md)):

1. **What happens when the gate itself is down, errors, or can't reach GitHub?** If it defaults
   to letting merges through (fail-open), an attacker can DoS or crash the gate to bypass it —
   availability becomes an authorization hole.
2. **Can the actor who authored a PR also approve/merge it?** GitHub's documented Actions
   bypass turns on multiple identities colluding (author = pusher = approver). If self-approval
   is possible, the human-approval loop is decorative.

Prior art: Kubernetes/OPA Gatekeeper admission control historically shipped fail-*open* only
because a single webhook replica made fail-closed a control-plane outage risk; the fix was ≥2
replicas, then flip to fail-closed.

## Options considered
1. **Fail-open** (merge proceeds if the gate is unavailable) — never blocks developers; but any
   outage/crash is a silent bypass. Unacceptable for a security control.
2. **Fail-closed** (merge blocked until the gate renders a verdict) — an outage blocks merges;
   mitigated by running ≥2 replicas + an audited break-glass.
3. **Self-approval allowed** vs **separation of duties** (approver ≠ author ≠ any commit pusher).

## Decision
**Fail-closed, with redundancy and an audited break-glass.** The required status check reports
`pending`/`failure` (never `success`) whenever the gate is down, errored, or unreachable; we run
≥2 worker replicas so fail-closed does not mean a permanent lockout; a break-glass override
exists but is rare, time-boxed, and loudly written to the audit ledger.

**Enforce separation of duties.** An agent-authored PR requires an *additional* human approver,
and `/agentgate approve` is refused (and audited) when the approver is the PR author or any
commit pusher. This composes with the existing write-access check ([ADR-001](001-approval-channel.md)).

## Consequences
- **Easier:** the security guarantee is honest — no outage or DoS is a bypass, and no single
  identity can both author and wave through a change.
- **Harder / to watch:** a gate outage blocks merges (hence the ≥2-replica requirement and a
  status page); break-glass is a real, intentional bypass and must be minimized and monitored;
  the "who is a distinct identity" check depends on robust actor identity (App attribution),
  which is itself Phase-1.5 scope.
- **Revisit:** if false-lockouts hurt developer trust, tune break-glass ergonomics — but never
  by flipping to fail-open.
