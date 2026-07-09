# 01 — Market research

*Snapshot: mid-2026. Figures are from third-party aggregators/press and may be stale —
treat as directional, not audited.*

## The layers, and where the wall is now

| Layer | Question | 2026 status |
|---|---|---|
| Observability / tracing | "What did the agent do?" | Crowded/funded — Arize, LangSmith, Langfuse |
| Eval / simulation | "Does it behave in tests?" | Crowded/funded — **Braintrust ~$800M val**, Maxim |
| Guardrails | "Is the *text* safe?" | Filling up — Galileo, Patronus |
| **Action authorization + accountability** | **"May this actor take *this action*, and can we prove it?"** | **OPEN — the next wall** |

## Adjacent incumbents (know who we're *not* fighting)

- **Eval/observability:** Braintrust (quality-management-system framing, ~$800M),
  LangSmith (LangChain-native), Arize (ML+LLM observability), Galileo, Langfuse (OSS),
  Maxim (simulation), Patronus (proprietary eval models). → We are **complementary**:
  they test/observe; we **enforce at runtime on actions**.
- **Agent identity / IAM:** Cisco Duo "Agentic Identity" (RSAC 2026), Okta, Strata,
  SecureAuth. → We **consume** identity ("who is the agent") and own the **action
  decision + approval + audit** they don't.
- **Enterprise agent platforms:** Decagon (~$4.5B val, ~$35M ARR), Sierra (Bret Taylor),
  Cognigy (acquired by NICE, ~$955M). → We **sell to their customers**, not compete.

## Demand signals (`anyagent pain2gain`, 138 real signals)

Top raw pains mined from HN/arXiv for *"teams can't trust their AI agents in production"*:

1. **Agent Vault** (open-source credential proxy/vault for agents); **Agent Passport**
   (OAuth-like identity verification for agents).
2. **AgentArmor** (agent security framework); an **"EU AI Act compliance layer for AI
   agents (8/2026)."**
3. **Trust Protocols** across Anthropic/OpenAI/Gemini.

Note the tell: the hottest demand is **identity / credentials / trust / compliance**, and
the players are **Show-HN open-source projects**, not $800M incumbents. The lane is early.

## Regulatory tailwinds (why the wall gets taller, fast)

- **EU AI Act** — fully applicable **Aug 2026**; demonstrable human oversight + audit trail
  become legal requirements for consequential automated decisions.
- **FINRA 2026** — flags autonomy, scope-creep, and **auditability** of multi-step agent
  reasoning as novel risks.
- **NIST AI Agent Standards** (Feb 2026) and **OWASP Top-10 for Agentic Apps** (2026).
- A 2025 scan found **every MCP server lacked authentication** — the plumbing for
  agents-that-act doesn't exist yet.

## Positioning

> **AgentGate = the action firewall + accountability ledger for agents-that-act.**
> Horizontal (any agent, any model), actor-aware (human + AI), compliance-native (audit
> trail maps to EU AI Act / FINRA). First wedge: PR firewall for coding agents.

## Open questions to validate (before scaling)

- **Buyer?** Platform eng vs. CISO vs. compliance owner — who holds budget?
- **$ TAM?** Bottom-up from "# of orgs running coding agents × seats/PR volume."
- **Willingness to pay** for a gate vs. rolling their own GitHub Action.
