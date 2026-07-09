# 04 — Security & threat model

AgentGate sits on the merge path, so it is itself a high-value target. Design assumes the
PR author (human *or* agent) may be adversarial.

## Trust boundaries

- **Inbound webhooks are untrusted** until the HMAC-SHA256 signature over the raw body is
  verified with the shared secret (constant-time compare). Unverified → `401`, no parsing.
- **PR content is untrusted** (diffs, titles, bodies). Never `eval`/execute it; checks read
  it as data only. The LLM reviewer must treat diff text as data, not instructions
  (prompt-injection: the diff cannot change the policy — policy lives outside the prompt).
- **The agent's own claims are untrusted.** Authorization derives from the verified GitHub
  actor + policy, never from what the PR says about itself.

## Threats → mitigations

| Threat | Mitigation |
|---|---|
| Forged/replayed webhook | HMAC verify + idempotency on `delivery_id` |
| Secret smuggled in a diff | `secret_scan` hard-block (request changes), not escalate |
| Agent edits its own guardrails | `src/agentgate/policy/**`, `.github/workflows/**`, `**/auth/**` are protected paths → escalate to human |
| Prompt injection via diff → coerce approval | Policy is data; LLM output is advisory and cannot raise privileges; risky + no LLM evidence ⇒ escalate |
| Tampering with the audit history | Hash-chained ledger; `audit/verify` re-walks and detects any edit/insert/delete |
| Over-broad agent autonomy | Actor-aware policy: agents auto-merge only low-risk; medium+ ⇒ human |
| Credential leakage | Secrets from env only, never logged; `.env`, `*.pem`, `*.key` git-ignored; container runs non-root |

## Secrets & least privilege

- No secrets in code or tests (CI would fail its own secret scan).
- GitHub App uses **short-lived installation tokens**, minted per-request in production
  (Phase 1), scoped to the minimum permissions (checks:write, pull_requests:write, contents:read).
- Container runs as a non-root user (see `Dockerfile`).

## Compliance posture (why the audit ledger matters)

The hash-chained ledger records, per decision: repo, PR, actor (+kind), action, risk,
reasons, and (Phase 1) approver identity + timestamp. This maps to **EU AI Act** (Aug 2026,
demonstrable human oversight) and **FINRA 2026** auditability. `audit/verify` provides a
tamper-evidence attestation.

## Known gaps (honest)

- Live GitHub token minting, LLM reviewer, and Redis worker are stubbed (Phase 1) — seams
  raise `NotImplementedError` rather than fake success.
- No multi-tenancy / RBAC yet (Phase 4). Not production-hardened for untrusted multi-org
  use until then.
