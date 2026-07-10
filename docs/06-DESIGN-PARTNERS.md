# 06 — Design partners & the 90-day pilot

The #1 non-R&D priority. Our own [`01-MARKET.md`](01-MARKET.md) names the unanswered question
that decides the company: **who holds the budget** for a gate on agent-authored code? Design
partners exist to answer that with money and behavior, not opinion. Be willing to be wrong.

> **Goal of this program:** 3–5 signed design partners in ~8 weeks, each running a 90-day
> pilot with **one measurable win**, so that by day 90 we know (a) the buyer, (b) whether they
> pay, and (c) the report/evidence format an auditor accepts.

---

## 1. The buyer hypotheses (the pilot is an experiment to decide between these)

| # | Buyer | Their pain | The signal that proves it's them |
|---|---|---|---|
| A | **Platform / DevEx eng lead** | "Coding agents open 20+ PRs/day; review doesn't scale; I don't want to hand-roll a GitHub Action" | They install the free App unprompted and ask for org-wide policy |
| B | **CISO / AppSec** | "Autonomous agents can touch prod, secrets, CI — I can't see or gate it" | They ask about the threat model, the Actions-bypass, SOC 2 |
| C | **Compliance / GRC owner** | "EU AI Act Art. 12 / SEC record-keeping — I must *prove* what AI did" | They ask for the audit export and whether their auditor accepts it |

**Test all three in every pilot** (one champion, but note who else shows up to the calls and who
signs the order). The buyer is whoever pulls the others into the room.

## 2. Ideal design-partner profile (ICP)

- **10–50 developers**, actively running coding agents (Copilot / Cursor / Devin / Claude Code)
  that open PRs — ideally ≥20 agent PRs/week (enough volume to feel the pain in 90 days).
- **A regulated vertical — fintech, health, insurance** — because EU AI Act / SEC / FINRA make
  "provable agent evidence" a *budgeted* line, not a nice-to-have. They feel the deadline first.
- On **GitHub** (our first integration), with branch protection they *think* is airtight.
- Has a named compliance function (even one person) — that's the budget signal.
- **Disqualifiers:** no agents in the SDLC yet (too early), or "we'll just build a GitHub Action"
  with no compliance pressure (won't pay).

## 3. Where to find them (highest-yield first)

1. **Warm intros** — the fastest path. Ask 10 people in your network for one intro each to a
   platform-eng or AppSec lead at a regulated-vertical company running coding agents.
2. **The GitGuardian move (distribution hack):** publish the free GitHub App + a short post/
   thread on the *Actions branch-protection bypass* (the [DEMO.md](DEMO.md) hook). Technical
   buyers who didn't know their repos are bypassable will raise their hand.
3. **Communities:** platform-engineering / DevSecOps Slacks & subreddits, "AI agents in the
   SDLC" threads, HN Show-HN of the demo, LinkedIn (your love12xfuture audience skews builder).
4. **Regulated-vertical AI-governance forums** — where the Art. 12 deadline is already a topic.

## 4. Outreach templates

Keep it short, lead with *their* pain, offer a specific artifact, ask for a 20-minute call. One
variant per buyer hypothesis — pick by title.

**A — Platform / DevEx lead (cold email):**
> Subject: gating the agent PRs, without hand-rolling a GitHub Action
>
> Hi {name} — teams your size are seeing coding agents (Copilot/Cursor/Devin) open dozens of
> PRs a day, and review doesn't scale. We built AgentGate: a PR firewall that knows whether a
> human or an agent authored a change and holds agents to a stricter bar — auto-approve the safe
> ones, route the risky ones to a human, log every decision. Free GitHub App, installs in
> minutes. Could I show you the 3-minute demo of it catching an agent rewriting CI? — Paul

**B — CISO / AppSec (cold email):**
> Subject: your branch protection is bypassable (here's the fix)
>
> Hi {name} — quick heads-up worth 3 minutes: GitHub branch protection can be bypassed via a
> workflow token (GitHub calls it "expected behavior"), so "we require reviews" isn't airtight
> once autonomous agents have write access. AgentGate closes that path and gives you a
> tamper-evident record of every agent decision. Happy to show the bypass live on a throwaway
> repo and how we block it. Worth a look? — Paul

**C — Compliance / GRC (warm-intro ask):**
> {name}, you mentioned the EU AI Act Article 12 logging obligation (Aug 2026) — AgentGate
> produces exactly that evidence for code changes: a tamper-evident, exportable record of every
> decision an AI agent's PR triggered, mapped to Art. 12. I'd love 20 min to check whether the
> export format is one your auditor would accept. Can you intro me to {champion}?

## 5. The 90-day pilot — one-pager (hand this to the partner)

> **Partner:** {company} · **Champion:** {name, title} · **Start:** {date}
>
> **Objective (one sentence):** prove AgentGate correctly gates {company}'s AI-agent PRs and
> produces audit evidence {compliance owner} accepts — in 90 days, on {N} repos.
>
> **Success metric (pick 1–2, measurable):**
> - ≥ **95%** of agent PRs receive the *correct* gate decision (spot-checked vs. human judgment);
> - **100%** of decisions land in a verifiable ledger (`audit/verify` → intact);
> - **≥1 real** risky change (secret / CI-rewrite / oversized diff / self-modifying policy) is
>   caught and routed to a human during the window;
> - the **compliance export is accepted** by {company}'s auditor/counsel as Art. 12 / SEC evidence.
>
> **In scope:** install the GitHub App on {N} repos; the hardened ruleset ([phase-1.5](specs/phase-1.5-non-bypassable.md));
> weekly 30-min check-in; a shared decision log.
> **Out of scope:** non-GitHub sources; multi-org RBAC; changing {company}'s existing CI.
>
> **Timeline:** Wk 1 install + baseline (how many agent PRs, current review load) · Wk 2–4
> shadow mode (gate observes + logs, doesn't block) to tune policy to *their* norms · Wk 5–10
> enforce (blocks + human-approval loop) · Wk 11–12 compliance export + readout.
>
> **What we ask in return:** a named reference / logo (if the metric is met), a 30-min weekly
> feedback loop, and permission to quote anonymized outcomes. **Price:** free during the pilot;
> a pre-agreed conversion price if the success metric is met (anchors willingness-to-pay).
>
> **Exit path:** at any time you can export your full audit ledger (JSON) and uninstall the App;
> we retain nothing. No lock-in during the pilot.

## 6. Tracking (keep it live)

| Company | Vertical | Champion (buyer hyp.) | Stage | Success metric | Result / learning |
|---|---|---|---|---|---|
| _example_ | fintech | Head of Platform (A) | pilot wk 4 | 95% correct gate | agents = 60 PRs/wk; CI-rewrites the top catch |
| | | | outreach / call / pilot / won / lost | | |

## 7. What we're really buying with this program
Not revenue yet — **evidence**: which buyer signs, what they'll pay, and the report format that
survives an auditor. Two of these three are still open questions in [`01-MARKET.md`](01-MARKET.md);
the pilots close them. Run founder-led (you close the first ~10 conversations) before any GTM hire.
