# The "caught in the act" demo

The shareable red-light moment: an AI coding agent tries to do something it shouldn't, and
AgentGate catches it, routes it to a human, and logs the whole chain in a tamper-evident
ledger. Three versions, from "runs right now" to "live on a real repo."

---

## 1. Offline demo (runs today, no setup) ▶️

Drives the **real** gate pipeline (`evaluate()` + the hash-chained `AuditLedger` — the same
code paths production uses), fully offline. No GitHub App, no network, no key.

```bash
make install
python scripts/demo_bypass_caught.py
```

Five scenarios, each decided by the deterministic policy:

| # | Actor & attempt | Outcome |
|---|---|---|
| 1 | Human — small clean bug fix | 🟢 **auto-approve** (the gate isn't just "no") |
| 2 | AI agent — smuggles an AWS secret | 🔴 **request changes** (hard block) |
| 3 | AI agent — rewrites CI (`.github/workflows/**`) | 🟠 **escalate → human** |
| 4 | AI agent — lands a 4,000-line diff | 🟠 **escalate → human** |
| 5 | AI agent — **edits its own policy file** | 🟠 **escalate → human** (the gate protects itself) |

Then it prints the hash-chained ledger, verifies it's `intact`, **and tampers with a record
to prove the chain breaks** (`verify → False`). The script exits non-zero if any decision
deviates from the expected outcome, so it doubles as an end-to-end smoke test.

**Why it lands:** #2–#4 are the obvious "bad agent" catches. **#5 is the differentiator** —
the agent's most elegant attack is to weaken the guardrails *in the same PR the gate is
judging*, and AgentGate treats its own policy file as a protected path, so that self-
substitution routes to a human. Screenshot the red lights + the tamper-detection line.

---

## 2. The bypass most teams don't know about (the credibility hook) 🎯

A live demo that a technical buyer respects: show that "we require a status check" is **not**
enough on GitHub by default.

**The attack (documented; GitHub calls it "expected behavior"):** GitHub branch protection
is bypassable via GitHub Actions. A write-capable actor can use the workflow `GITHUB_TOKEN`
to approve and merge its own PR — the `github-actions` bot counts as a *different* identity —
and a three-identity collusion (author, pusher, approver) defeats "author ≠ approver."
(Source: Mercari engineering, 2024.) **If an attacker bypasses branch protection, they
bypass the gate** — so a firewall that ignores this is theater.

**AgentGate's answer** (see [`docs/specs/phase-1.5-non-bypassable.md`](specs/phase-1.5-non-bypassable.md)):
we don't just post a check — we make the gate the *only* path and verify it:

1. **Rulesets, configured correctly:** required AgentGate check, *disable* "Allow Actions to
   create/approve PRs," *require approval of the most recent push,* merge queue so checks
   re-run against the real post-merge tree.
2. **CODEOWNERS** on the policy file and the gate's own code — so scenario #5 above can't be
   merged without a human owner even if every other check is green.
3. **Fail-closed:** if the gate is down or errors, the required check reports pending/failure
   → merge stays blocked. It never emits a pass on error.
4. **A repo-config verifier** that inspects a repo and reports each open bypass as a finding.

The demo: on a normally-configured repo, run the bypass → merge succeeds (💥). Turn on
AgentGate's hardening → run the same bypass → **blocked**, with the attempt in the ledger.

---

## 3. Live on a real repo (needs a GitHub App) 🔜

The end-to-end "founder screen-record." Requires Phase-1 credentials
([`docs/specs/phase-1-github-loop.md`](specs/phase-1-github-loop.md)): a GitHub App
(`GITHUB_APP_ID` / private key / installation id) installed on a throwaway repo with the
hardened ruleset above.

1. `cp .env.example .env` and set the App creds + `GITHUB_WEBHOOK_SECRET`; `make docker-up`.
2. Open an **agent-authored** PR that (a) rewrites CI, or (b) adds a secret, or (c) is 4k lines.
3. Watch AgentGate post a **check-run that blocks merge** + a review + a comment with reasons
   and an **audit id**.
4. A human with write access comments `/agentgate approve`; AgentGate verifies their
   permission, flips the check to success, and records approver + timestamp.
5. `GET /audit/verify` → `{"intact": true}`. Export the window as the compliance artifact.

> **Status (honest):** version 1 runs today; versions 2–3 depend on the Phase-1.5 hardening
> and live GitHub App wiring, which are specced but not yet live-verified against a real repo.
