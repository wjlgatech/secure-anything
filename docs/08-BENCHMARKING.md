# 08 — Benchmarking AgentGate (effectiveness · efficiency · scalability · safety)

*Added 2026-07-21. Answers: do we need a benchmark, on what axes, against whom — and how to keep it
from being vanity/self-graded. Tier-1 harness is real and runnable (see the lifescience-os pilot
`pilots/agentgate-gxp/benchmark.py`); Tier-2/3 are designed here.*

## Do we need it? Yes — for three specific reasons

1. **The ROI claim is unprovable without it.** The whole pitch is "verification cheaper than redoing."
   That is a *measured* claim (auto-clear rate × review-time saved, latency, cost) — assert it and a
   buyer's data-science team breaks it in the room.
2. **Our own trust ladder demands it.** We hold others' claims to L4 (measured/faithful); AgentGate's
   claims about itself must clear the same bar. A benchmark is how "the gate works" becomes L4.
3. **The category has no standard benchmark** (see `01-MARKET.md`: "action authorization +
   accountability" is the open wall). Publishing a reproducible one is thought-leadership — *and* a
   moat, if it's independent.

**Two traps to design out (both from the 3-horizon research in `09-TRUST-AS-A-SERVICE.md`):**
- **Vanity metrics** — Gartner: >40% of agentic projects get cancelled; benchmark *decisions that
  matter*, not a leaderboard number. Report the cost side (false-escalation rate), not just catches.
- **Issuer-pays capture** — the #1 300-year failure mode (Moody's→2008). A benchmark we grade
  ourselves is worth nothing. The corpus + harness must be **open and reproducible** (exit-0 gate,
  runnable by anyone), ideally third-party-run. That independence *is* the credibility.

## The four axes → concrete metrics

| Axis | Metric | How | Tier |
|---|---|---|---|
| **Effectiveness** | decision accuracy vs a labeled corpus (precision/recall/F1 per label); real-world **catch rate** on malicious PRs; **false-escalation rate** (the cost side) | labeled changeset corpus; adversarial red-team corpus | T1 (correctness) · **T2 (catch rate)** |
| **Efficiency** | per-decision **latency** (p50/p95); **human-review-hours saved / 100 PRs**; **$/decision** | time the core; field study for hours-saved | T1 (latency) · T4 (field ROI) |
| **Scalability** | throughput (decisions/sec); burst/queue behavior at 10 / 50 / 500 PRs·day; Redis worker path | load harness against the worker | **T3 (load)** |
| **Safety** | **non-bypassability** (can the judged code disable the gate? self-approval refused?); **tamper-evidence** (ledger integrity under mutation); **adversarial robustness** (does a prompt-injected diff / jailbroken agent slip through?); **fail-closed** on evaluator error | adversarial suite; the Phase-1.5 `audit-repo` bypass report | **T2 + Phase-1.5** |

## Tier-1 (built, real numbers — 2026-07-21)

Ran `benchmark.py` on the real core with the GxP policy pack (`pilots/agentgate-gxp/`):
- **Effectiveness (correctness):** decision accuracy vs policy = **16/16 = 100%**, zero
  misclassifications across approve/escalate/block × human/agent × GxP-path/secret/churn/boundary
  cases. *Honest read: this measures engine-matches-its-policy-spec (a regression/no-drift bar) — it
  is NOT a real-world malicious-catch rate. That is Tier 2.*
- **Efficiency (latency):** p50 **0.028 ms**, p95 **0.034 ms**, ~**39k decisions/sec** single
  process, offline core. So the deterministic core is effectively free vs a ~15-min human review.
  *Caveat: adding the optional LLM-reviewer will dominate latency — re-measure that path separately.*

## Tier-2 (BUILT 2026-07-21, real numbers): adversarial catch rate

An 18-case red-team corpus with ground-truth intent (12 malicious/risky, 6 benign), run on the real
core (`lifescience-os/pilots/agentgate-gxp/redteam.py`). Reports catch rate + false-escalation rate.
**Built to include attacks the deterministic core cannot catch — a red-team that scores 100% is rigged.**

| Policy | Catch rate | False-escalation | Precision | F1 |
|---|---|---|---|---|
| Baseline GxP pack | **7/12 = 58%** | 0/6 = 0% | 100% | 0.74 |
| Hardened (policy-only, +auth/manifest paths) | **9/12 = 75%** | 0/6 = 0% | 100% | 0.86 |

**Findings (honest):**
- **Policy-as-data pays off:** hardening the *YAML* (adding `**/auth/**` + dependency manifests)
  caught the auth-backdoor and supply-chain-typosquat cases — **+17 pts catch rate, zero code, zero
  new false escalations.**
- **Measured safety strength:** a prompt-injection-in-PR-body ("IGNORE POLICY, AUTO-APPROVE") with a
  benign diff was correctly auto-approved — the deterministic core ignores injection text. Structural
  prompt-injection resistance, measured.
- **3 residual misses need code (the roadmap driver):** obfuscated/split-string secrets → an
  **entropy/obfuscation-aware secret check** (new deterministic check); a semantic logic backdoor
  (small, unprotected, no secret) → the **LLM reviewer (Phase 2)**, gated so "no evidence ⇒ escalate."
- **Bottom line:** deterministic policy catches *structural* attacks (secrets, protected paths, CI
  tamper, size, +supply-chain/auth once hardened); *semantic* attacks need the LLM layer — which must
  itself be gated or it reintroduces the non-determinism we removed.

Precedent to grow toward: Lakera *Gandalf* + *HackAPrompt* (prompt-injection corpora); add ≥2
independent labelers + Cohen's κ (trust-ladder L6) and run in CI on every gate change.

## Tier-3: the competitor capability matrix (who they are)

There is **no apples-to-apples rival** — the exact cell "may THIS ACTOR take THIS ACTION, and can we
prove it?" is open (`01-MARKET.md`). So the honest comparison is a **capability matrix**, not one
score. Based on public product positioning (not hands-on testing — flagged WEAK until we bench them
directly):

**The competitor set, by category:**
- **Policy / authorization engines** — Open Policy Agent (OPA/Rego), AWS **Cedar**, **Oso**,
  **Permit.io**. Policy-as-code, yes — but not actor-aware *for AI agents*, not PR/action-native, no
  tamper-evident ledger, no risk-tiering.
- **PR gate / code scanning** — GitHub **branch protection + required checks + CODEOWNERS**,
  **GitGuardian** (secrets), **Semgrep**/**Snyk** (SAST). Scan/gate on *content*; not actor-aware
  authorization + court-grade audit of the *decision*.
- **AI PR reviewers** — **CodeRabbit**, **Greptile**, **Graphite Diamond**, **Qodo**. LLM review
  quality; *advisory*, non-deterministic, no policy firewall, no ledger.
- **AI security / runtime** — **Lakera** (Check Point), **Robust Intelligence** (Cisco AI Defense),
  **Protect AI** (Palo Alto, Prisma AIRS), **HiddenLayer**. Secure the model / prompt / runtime I/O;
  not per-action authorization on consequential actions with an audit chain.
- **Agent identity / IAM** — **Okta**, **Cisco Duo** agentic identity, **Astrix**, **Token Security**.
  Answer "who is the agent"; AgentGate *consumes* identity and owns the action decision + approval +
  audit they don't.
- **Eval / observability** — Braintrust, Arize, LangSmith, Langfuse, Galileo, Patronus, DeepEval.
  **Complementary, not competitors**: they produce behavior evidence AgentGate can gate on.

**Matrix dimensions (score each tool 0/◐/●):** actor-aware (human vs AI-agent bar) · policy-as-data
(not prompt) · deterministic/prompt-injection-proof core · per-action authorization · tamper-evident
audit ledger · human-approval with verified write-access · non-bypassable enforcement · regulated
(GxP/Part 11 / EU AI Act) mapping. AgentGate's thesis is that it is the only one marking ● across the
*combination* — the matrix is how we show it without a fake head-to-head number.

## Recommendation

1. **Ship T1 open** (done — reproducible, exit-0) as the credibility anchor.
2. **Build T2 red-team corpus next** — it is the real "does it work" number and where policy-as-data
   should win measurably.
3. **Publish the T3 capability matrix** honestly (positioning-based, flagged), and invite
   independent runs of T1/T2 — turning "trust us" into "run it yourself," the anti-issuer-pays moat.
4. Keep the cost side (false-escalation rate) in every report; a gate that escalates everything is
   "secure" and worthless.

*Sources for the market/competitor context: `09-TRUST-AS-A-SERVICE.md` (primary-cited) + `01-MARKET.md`.
Competitor capability claims here are from public positioning, not hands-on evaluation — WEAK until
benched directly.*
