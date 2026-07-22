# 07 — Prior art: the USC FORTIS Lab (AEGIS + agent-audit)

*Source-level comparison, 2026-07-18. Both repos cloned and read (not just their READMEs).
This is the closest prior art to AgentGate found to date — same thesis, adjacent chokepoints.*

## TL;DR

Dr. **Yue Zhao**'s USC **FORTIS Lab** (Foundations Of Robust Trustworthy Intelligent Systems —
author of PyOD/TrustLLM, 60+ papers) ships two open-source tools that bracket AgentGate on either
side of the software lifecycle:

- **`agent-audit`** (Heady Zhang) — a **build-time** static scanner (SAST) for agent *code*.
- **AEGIS** — a **runtime** pre-execution firewall for agent *tool calls*, with a published,
  benchmarked paper ([arXiv 2603.12621](https://arxiv.org/abs/2603.12621), EMNLP).

Neither gates the **merge/PR chokepoint**, and neither is **actor-aware** (human vs AI-agent vs
bot). **That is AgentGate's wedge, and it is uncontested by the most credible group in the space.**

The honest flip side: on **audit cryptography** and **policy expressiveness**, AEGIS is *ahead* of
AgentGate today. See "Where we're behind" below — it drives [ADR-003](adr/003-ed25519-audit-signing.md).

## The three tools are three chokepoints on one lifecycle

```
   BUILD TIME              MERGE TIME                 RUN TIME
   (scan the code)         (gate the change)          (gate the action)
 ┌───────────────┐      ┌────────────────────┐      ┌──────────────────┐
 │  agent-audit  │      │    AgentGate  ★     │      │      AEGIS       │
 │  SAST / SARIF │  →   │  PR firewall,      │  →   │ tool-call        │
 │  OWASP rules  │      │  actor-aware       │      │ firewall, runtime│
 └───────────────┘      └────────────────────┘      └──────────────────┘
   FORTIS Lab             ← us →                       FORTIS Lab
```

They are **complementary, not substitutes** — an org could run all three. AgentGate owns the middle
chokepoint that neither FORTIS tool touches.

---

## AEGIS — the one that matters (runtime firewall)

Repo: [`Justin0504/Aegis`](https://github.com/Justin0504/Aegis) · MIT · paper: arXiv 2603.12621
(Aojie Yuan, Zhiyuan Su, Yue Zhao).

**One-liner (theirs):** *"The firewall for AI agents. Every tool call. Intercepted. Classified.
Blocked — before it executes."* — near-identical to AgentGate's thesis, one layer down.

### Architecture (from source)

- **Monorepo** (turbo), polyglot: TypeScript + Python + Go.
  - `packages/`: `gateway-mcp` (the core engine), `core-schema`, `cli`, `sdk-python`, `sdk-js`, `sdk-go`.
  - `apps/`: `compliance-cockpit`, `control-plane`, `desktop` (Tauri — ships a 164 MB `.dmg`), `marketing`.
  - Deploy surface: Docker, Helm/Kubernetes, fly.toml, railway.json, render.yaml, Homebrew, nginx,
    monitoring. On PyPI (`agentguard-aegis`) and npm (`@justinnn/agentguard`). **Production-grade.**
- **Runtime interception** (`sdk-python/agentguard/interceptors/`: `llm`, `stdio`, `auto` +
  `integrations/langchain`): wraps the tool-execution path and blocks *before* execution. 3-stage
  pipeline per the paper: deep string extraction → content-first risk scan → composable policy
  validation. Benchmarks: 48/48 attacks blocked, 1.2% FP on 500 benign calls, 8.3 ms median latency.
- **Policy engine** (`gateway-mcp/src/policies/policy-engine.ts`): **multi-tenant**, storage-agnostic
  (`SqlitePolicyStore | PostgresPolicyStore`), **AJV JSON-schema** validated, per-org cache with
  wildcard/tenant-shadow semantics. A **policy DSL** (`core-schema/src/policy-dsl.ts`) *and* a
  **natural-language → policy compiler** (`services/nl-policy-compiler.ts`). A `classifier`
  categorizes each tool call (database/file/network/…) and maps categories → policy families.
- **Tamper-evident audit — a superset of ours:**
  1. **Trace hash-chain** — `previous_hash → integrity_hash`, with `validate_hash_chain()` in
     `core-schema` (Python + TS). Same primitive as our ledger.
  2. **Content hash** — canonical SHA-256 over the trace tuple `{input_context, thought_chain,
     tool_call, observation}` (`services/content-hash.ts`), versioned so rows can't silently reorder.
  3. **Ed25519 signatures** — `sdk-python/agentguard/crypto/signing.py` signs traces;
     `gateway-mcp/src/services/signing.ts` produces **detached-signed evidence packs** a SOC 2
     auditor verifies offline (self-contained: PEM pubkey embedded, `key_id` = 8-char SHA-256 prefix).
- **Enterprise surface:** kill switch, approvals store, supply-chain scan, proxy interception (for
  *closed-source* agents), MCP gateway (Claude Desktop/Code), OpenTelemetry, SIEM fan-out
  (`AuditLogService` subscribers), admin audit log with SOC2/ISO27001/HIPAA/FedRAMP framing,
  `COMMERCIAL.md` (dual-license play).

### Scope boundary (our opening)

AEGIS gates **tool calls at runtime**, framework-integrated. The paper states it **does not cover
code review or pull-request stages**. It has no notion of *who authored a change* (human vs agent) —
it classifies the *tool call*, not the *actor*. Both gaps are AgentGate's core.

⚠️ **Watch signals of drift toward our lane:** the repo already ships a `Code Shield` feature and a
`predeploy.scan` audit action — evidence they may extend leftward. Move fast on the wedge.

---

## agent-audit — build-time SAST (complementary; a candidate *check*)

Repo: [`HeadyZhang/agent-audit`](https://github.com/HeadyZhang/agent-audit) · MIT · Python/poetry ·
1541 tests.

- **Static analysis** of agent code: taint tracking from **tool boundaries** to dangerous sinks
  (`subprocess`/`eval`), **MCP config auditing**, entropy-based secret detection, framework
  detection, a confidence matrix, and **allowlists** that de-escalate framework-standard patterns to
  cut false positives.
- **Rules:** ~39+ `AGENT-xxx` rules across builtin packs — `owasp_agentic` (+v2), `mcp_security`,
  `asi_coverage`, `langchain_security`, `agent_architecture` — plus a **MITRE ATLAS** mapping.
- **CI-native:** GitHub Action (`action.yml`) emitting **SARIF**/json/markdown with a `fail-on`
  severity gate.

**Opportunity:** agent-audit is exactly an `EvidenceCollector` in our sense. Wrapping it as an
AgentGate **check** (`src/agentgate/checks/`) gives us a 39-rule, OWASP-mapped SAST signal inside the
PR gate for near-zero build cost — a fast credibility win and a concrete reason to talk to the lab.

---

## Where AgentGate stands — honest scorecard

| Dimension | agent-audit | AEGIS | **AgentGate** |
|---|---|---|---|
| Chokepoint | build-time (code) | runtime (tool calls) | **merge-time (PRs)** ← uncontested |
| Actor-aware (human/agent/bot) | no | no | **yes** ← unique |
| Policy | rule packs | multi-tenant DSL + NL compiler | single-file YAML (simpler) |
| Audit: hash-chain | n/a | ✅ | ✅ |
| Audit: content-tuple hash | n/a | ✅ | ❌ |
| Audit: **Ed25519 signatures / evidence pack** | n/a | ✅ | ❌ → [ADR-003](adr/003-ed25519-audit-signing.md) |
| Maturity / GTM | PyPI + Action | desktop app, control plane, multi-cloud, commercial | pre-Phase-2 |
| Pure, offline-deterministic core | partial | no (service-heavy) | ✅ ← our discipline edge |

**Where we're ahead:** the actor-aware merge chokepoint; policy-as-data simplicity; a genuinely pure,
offline-testable decision core.
**Where we're behind:** audit crypto (they chain **and** content-hash **and** sign; we only chain),
policy expressiveness, and product/GTM maturity. Do **not** chase their runtime-firewall or
policy-DSL surface — that's their moat. Win merge-time decisively instead.

---

## Recommended actions

1. **Reframe the market doc** — AEGIS is *validation* (a peer-reviewed group converged on our thesis)
   **and** a same-lane OSS peer at the runtime layer. Positioning: *"AEGIS gates what an agent does at
   runtime; AgentGate gates what an agent tries to merge — same accountability spine, different
   chokepoint, and we're actor-aware."* (done — see [01-MARKET.md](01-MARKET.md).)
2. **Close the audit-crypto gap** — adopt Ed25519 signing of chain heads / signed evidence export.
   See [ADR-003](adr/003-ed25519-audit-signing.md). This is the single highest-credibility upgrade and
   directly serves Phase-2 "external anchoring."
3. **Wrap agent-audit as a check** — SARIF evidence collector in the PR gate (Phase 2+). Cheap, and a
   natural collaboration hook.
4. **Engage FORTIS** — cite the AEGIS paper in `00-BACKGROUND.md`; pursue a listing in the lab's
   [`awesome-auditable-ai`](https://github.com/yzhao062/awesome-auditable-ai) (Tools & Platforms) —
   free distribution to exactly our buyer. Heady Zhang / Yue Zhao are plausible design partners or
   research collaborators, not just competitors.
5. **Monitor** AEGIS `Code Shield` / `predeploy.scan` for leftward drift into the merge chokepoint.

## Sources

- AEGIS repo: https://github.com/Justin0504/Aegis · paper: https://arxiv.org/abs/2603.12621
- agent-audit repo: https://github.com/HeadyZhang/agent-audit
- FORTIS Lab / Yue Zhao: https://viterbi-web.usc.edu/~yzhao010/ ·
  curated list: https://github.com/yzhao062/awesome-auditable-ai
