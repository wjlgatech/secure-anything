# 07 — Trust & Safety as a Service (3-horizon research)

*Added 2026-07-21. Extends `01-MARKET.md` with a wide→deep survival-test read (30 days / 30 years /
300 years) of the "trust & safety as a service" opportunity, and how AgentGate maps to it. The
regulated/Life-Sciences application is developed further in a separate Accenture-context memo;
this file stays about AgentGate's own positioning. Citation-rigor standard: primaries cited;
funding/market figures flagged WEAK; historical→AI analogies flagged SPECULATIVE.*

## Why this doc

A prospective buyer's real objection to any AI trust tool: *"validating the agent's output takes
longer than doing it myself."* That single sentence is the market. A trust product is only a
business when **checking is cheaper than redoing** — the margin every durable verification
institution has won on for 300 years. This doc records what survived, and what it implies for the
gate.

## Wide (/last30days) — the market has a name and is consolidating

**AI TRiSM** (AI Trust, Risk & Security Management). Three layers, all bets on lowering verification
cost: **runtime guardrails** (Llama Guard arXiv:2312.06674, NeMo Guardrails arXiv:2310.10501,
Guardrails AI), **eval/faithfulness-as-a-service** (Patronus Lynx + HaluBench, Galileo, Arize,
Braintrust, DeepEval), **governance** (Credo AI, Holistic AI → NIST AI RMF / ISO 42001 / EU AI Act).

**"What enterprises buy" signal:** the *security* layer is being bought by incumbents — Cisco/Robust
Intelligence (Aug 2024), **PANW/Protect AI $634.5M verified** (Jul 2025, PANW 10-K), Check
Point/Lakera (Sept 2025). **The `01-MARKET.md` thesis holds:** observability/eval/guardrails are
crowding; **action authorization + accountability is still the open wall** — and it's exactly what
those incumbents *don't* own (they test/observe/secure the model; none owns the per-action decide +
approve + tamper-evident audit).

**Demand catalyst:** EU AI Act (Reg. (EU) 2024/1689) high-risk obligations enforceable **2 Aug 2026**.
Certify-against standards: NIST AI RMF 1.0, NIST GenAI Profile (NIST.AI.600-1), ISO/IEC 42001:2023.
Market-size numbers are analyst-divergent (~$2.7–4.9B 2025; a Gartner ~$3.1B→$13.8B figure only via
aggregators) — **WEAK, direction GROUNDED**.

## Deep (/last30years + /last300years) — the durable principles AgentGate must embody

The survivors of assurance (IV&V/IEEE 1012, Common Criteria, GSN assurance cases, GAMP 5, SOC 2) and
of third-party trust (chartered audit 1854, Lloyd's underwriting 1688, UL mark 1894/1906, Moody's
1909, FDA 1938) converge on five build-in principles and one design-out failure mode.

**Build in — and where AgentGate already does:**
1. **Independence is the product** (IV&V) → the gate is separable from the code it judges (Phase 1.5
   non-bypassable: "protect the gate from the code it judges; self-approval refused").
2. **Skin in the game / liability** (Lloyd's) → *gap*: a verdict carries weight when the verifier is
   accountable. Today the ledger records the human approver's verified write-access; a paid service
   would need explicit accountable sign-off (a named, revocable attestor).
3. **A portable, honestly-scoped mark amortizes trust** (UL) → the signed audit export (Phase 2) is
   the mark; scope must be stated so "gate-passed" doesn't over-signal.
4. **Audit the argument, not just the verdict** (GSN) → *build target*: export the ledger as a GSN
   assurance case, evidence → claim, so a reviewer audits the reasoning.
5. **Risk-proportionate, re-examinable evidence** (GAMP 5, 21 CFR Part 11) → policy-as-data +
   hash-chained ledger already give a deterministic, re-examinable record.

**Design out — the #1 failure mode in the entire 300-year record: issuer-pays capture.** Moody's →
2008: the party being rated pays the rater; FCIC (2011) called the agencies "key enablers." *"Whoever
pays for the verdict eventually shapes it."* AgentGate's structural antidotes, already on the
roadmap, are its strongest moat story: **external WORM/timestamp anchoring** (Phase 2 — the chain
head is corroborated *outside* the operator, so even the operator can't silently rewrite it) and a
**non-bypassable, self-approval-refused** gate (Phase 1.5). Lead with these; they are what a
credit-rating-shaped competitor cannot easily claim.

**The honest technical gap:** every surviving certificate (EAL, one-time SOC 2) assumes a *static
target*; agents are non-deterministic and self-modifying, so a one-shot stamp is **SPECULATIVE** for
agents. The defensible shape is a **living certification** — an assurance case whose evidence
includes continuous monitoring + independent red-teaming, not a dated badge.

## Implication for the roadmap (no new phases — sharper framing of existing ones)

- **Phase 2 (Trust & compliance)** is the T&S-aaS core: signed audit export = the *mark*; external
  anchoring = the *anti-issuer-pays moat*; add a **GSN assurance-case export** mapped to ISO 42001 /
  NIST GenAI Profile / EU AI Act Annex III as the reusable artifact a buyer relies on instead of
  re-doing review.
- **Phase 3 (general action firewall)** is what lets the same core gate a *regulated* action (a
  submission, a prod mutation), not just a PR — the doorway to regulated verticals.
- **Phase 4 GTM:** the only ROI framing that clears the buyer's objection is **substitute for manual
  review/validation spend** (in regulated industries, GxP/CSV labor) — a line item that already
  exists, so "cheaper than redoing" is provable, not asserted.

## Sources (primary; funding/market flagged)

Llama Guard arXiv:2312.06674 · NeMo Guardrails arXiv:2310.10501 · PANW 10-K (Protect AI $634.5M)
https://www.sec.gov/Archives/edgar/data/1327567/000132756725000027/panw-20250731.htm · Cisco/Robust
Intelligence https://blogs.cisco.com/news/fortifying-the-future-of-security-for-ai-cisco-announces-intent-to-acquire-robust-intelligence
· Check Point/Lakera https://www.checkpoint.com/press-releases/check-point-acquires-lakera-to-deliver-end-to-end-ai-security-for-enterprises/
· EU AI Act Reg 2024/1689 https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:L_202401689 · NIST
GenAI Profile https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf · ISO/IEC 42001 https://www.iso.org/standard/42001
· IEEE 1012-2024 https://standards.ieee.org/ieee/1012/5609/ · GSN Community Standard v3 https://scsc.uk/gsn
· GAMP 5 2nd ed https://ispe.org/publications/guidance-documents/gamp-5-guide-2nd-edition · SOC 2 (AICPA)
https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services
· UL history https://ul.org/about/our-history/ · Moody's/issuer-pays/FCIC https://www.cfr.org/backgrounders/credit-rating-controversy
· Lloyd's (1688) https://www.lloyds.com/about-lloyds/history/coffee-and-commerce · FDA 1938 https://www.fda.gov/about-fda/changes-science-law-and-regulatory-authorities/part-ii-1938-food-drug-cosmetic-act
