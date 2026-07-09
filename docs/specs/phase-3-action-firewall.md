# SPEC — Phase 3: General Action Firewall  (Status: ⬜ Planned)

## Goal
Generalize from "PR" to **any consequential action**. The same core (policy → decision →
approval → audit) gates tool calls like payments, DB writes, mass emails, and agent-to-agent
requests.

## User stories
- As an agent developer, I route a risky tool call through AgentGate and get
  approve / deny / escalate + an audit record, with ~no code change.
- As a security owner, high-risk actions require scoped, short-lived, revocable credentials
  and a human approval that's logged.

## In scope
1. **Action proxy / MCP shim**: a thin SDK + an MCP-server front so agents call
   `gate(action)` (or route MCP tool invocations) through the same decision core.
2. **Action schema**: generalize `PullRequest`/`ChangeSet` → `Action{kind, actor, payload,
   risk_signals}`; checks become action-type-aware.
3. **Identity consumption**: accept an external verified agent identity (Cisco Duo / Okta /
   MCP auth) instead of inferring — authorization derives from it.
4. **Scoped credentials**: issue short-lived, attenuated, revocable tokens per approved
   action; preserve the delegation chain (who began the request, which agent, under what grant).

## Out of scope
Full IAM (we consume it, not build it); GTM (P4).

## Task checklist
- [ ] Generalize domain types to `Action`; keep PR path as one action type.
- [ ] MCP shim + SDK client; example: gate a mock payment tool call.
- [ ] External identity adapter (one provider first).
- [ ] Per-action credential issuance + revocation + delegation-chain fields in the ledger.
- [ ] Tests: mock-payment action escalates + audits through the same core.

## Definition of Done
A non-GitHub action (mock payment above a threshold) is escalated, approved by a human, and
recorded in the same audit ledger — proving the core is action-agnostic.

## Risks / open questions
- Latency budget for inline action gating (must be low for tool calls).
- Which identity provider first; MCP auth is still nascent.
