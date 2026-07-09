# 00 — Background: how we got here

*Preserved so the "why" outlives the chat that produced it.*

## The path

1. **We built on Juji.** Hands-on: wrote its REP scripting, drove its GraphQL + WebSocket
   API, white-labeled a restaurant agent, and debugged it live (a generative-fusion
   duplicate-message bug, case-sensitive matching, a flow-control race where input sent
   before the opener got swallowed). Real signal, not a datasheet read.

2. **We judged the product.** Juji's genuine strength is a *thesis*: **combine
   deterministic guarantees with generative flexibility** — scripted exactness where it
   matters, LLM fluency where it helps. Its weakness: an aging stack and a paradigm
   (flow-charts, personality inference) that the market has moved past. Verdict: **do not
   clone Juji.** Steal the thesis, not the code.

3. **We scanned the market.** The obvious idea — "test/observe your AI agent" — is already
   a funded knife fight: **Braintrust (~$800M val)**, LangSmith, Arize, Galileo, Langfuse,
   Maxim, Patronus. Eval/observability/guardrails is *closing*, not opening.

4. **We found the next choke point.** As agents shift from **talking → doing** (merging
   code, moving money, mutating systems), the bottleneck moves from *"is the text safe?"*
   to **"is this actor allowed to take *this action*, on whose authority, and can we prove
   it later?"** That layer barely exists.

5. **Three independent instruments agreed.** Our firsthand read, the market scan, **and**
   the `pain2gain` engine (138 real signals) all pointed at the same place: the top raw
   demand was **agent identity / credentials / trust / EU-AI-Act compliance layers**, not
   eval. (See [01-MARKET.md](01-MARKET.md).)

## The thesis (Juji's, flipped and aimed at the open lane)

> **Verifiable + flexible, applied to *actions*.** Give teams LLM-native flexibility with
> *hard* guarantees, human approval, and provable accountability where it matters — for
> **both human and AI-agent actors**.

Be the **arms dealer**, not a combatant: a horizontal gate that works with *any* agent and
*any* model, sold to everyone building or deploying agents — not another agent builder
fighting Sierra/Decagon.

## The wedge: a PR firewall for coding agents

The sharpest, most concrete first action to gate is **a coding agent opening a pull
request** — because "10–50 developers + coding agents shipping daily PRs" is a pain teams
have *today*, it's demoable, and it rides three regulatory tailwinds landing Aug 2026
(EU AI Act), plus FINRA and NIST agent-oversight guidance.

**The viral demo:** watch an agent try to merge a secret / rewrite CI / land a 4,000-line
diff — and the gate catch it, route it to a human, and log the whole chain. Red light,
screenshot, share.

## Why us

The design DNA is a **ClosedLoop**: *collect evidence → score → gate → block on fail*
(the spine of the `anyagent` engine and its BRACE control-evidence mode). AgentGate
re-points that gate from "gate a build" to "gate a live agent action." Not a pivot — the
same weapon, aimed at an open target.

## Honest caveats

- `pain2gain` is a **demand proxy, not a $ TAM**; its signal skewed to HN/arXiv (Reddit/X/
  finance sources were rate-limited/keyed). Bottom-up sizing + 5 buyer interviews still owed.
- IAM incumbents (Cisco Duo, Okta, Strata) are grabbing agent *identity*. We must stay in
  the **action-decision + approval + audit** lane and *consume* their identity, not fight it.
