# REPO_PLAYBOOK — how a Paul Wu `-anything` / `-os` repo is built

> **Building a META-repo (super-repo/super-tool that composes other repos)?** This file still
> governs the mechanics, but read `META_REPO_PLAYBOOK.md` (same folder) FIRST — charter before
> scaffold: VISION/mission/north-star, composition doctrine, and the milestone arc.

> **Canonical single source.** This file lives in `Projects/_templates/` and is seeded into
> every new repo by `new-project.sh` (as `docs/REPO_PLAYBOOK.md`). Edit it HERE; the copies in
> repos are instances. Earned across design-anything, graph-engineering-anything,
> reverse-engineering-anything, strategize-anything, and research-anything.

## 0. Two project shapes — pick first

| Shape | When | CLAUDE.md template | Publishing |
|---|---|---|---|
| **Content / publishing** (default) | public build with a LinkedIn/X/portfolio launch | `_templates/CLAUDE.md.template` | LinkedIn docs + portfolio-first flow |
| **Private engineering** | private repo, spec-first build | `_templates/CLAUDE.md.private-engineering.template` | NONE (a publish flow in a must-stay-private repo invites accidental exposure) |

Record any deviation from either shape in the project's decision log.

## 1. The shape (what every repo has)

```
<name>/
├── GOAL.md              10x contract: verbatim intent → eval → the 10x move → milestone table
├── Makefile             `make check` = the offline, deterministic finish line
├── data/*.yml           the SINGLE SOURCE OF TRUTH (spec-as-data). Nothing hand-edited downstream.
├── docs/                ARCHITECTURE · SPEC · ROADMAP · LANDSCAPE · REPO_PLAYBOOK (this file)
├── src/<pkg>/           the OOP engine (typed models + single-responsibility services)
├── scripts/             thin CLIs over the engine (logic lives in src, never in the CLI)
├── tests/               pytest; every gate has an executable test
├── skills/              the flagship thin-router skill + generated satellites (if it composes repos)
├── research/            window-dated digests (30 days / months / years / 300 years) — if research-shaped
├── llms.txt · README (with a drift-gated News block) · CHANGELOG · CONTRIBUTING · CLAUDE.md
└── .github/workflows/   check.yml (gate) + a weekly, human-gated sync (if it tracks upstreams)
```

## 2. The non-negotiable disciplines (each becomes a `data/ainative.yml` principle)

- **spec-as-data** — curated knowledge lives in `data/*.yml`; every published surface (README
  sections, skills, contracts) is GENERATED and **drift-gated** (`build --check`).
- **ready-is-a-gate** — the repo's domain has a definition of "done" as a machine gate with exit
  codes (design=geometry; research=claim-gate; a doc phase=a manifest gate). A gate never vibes.
- **no-evidence-means-no** — an unmeasured/unreachable item is excluded, never a fake pass; a
  blocking gate cannot pass on unmeasured items.
- **maker-is-not-checker** — generators and gates are independent, held together by tests.
- **satellites, never vendored** — a cited external repo is a pointer + a SHA-pinned digest + a
  generated thin skill; freshness is *measured* (STALE flag), not promised.
- **compounding-memory** — updates and lessons land in `data/` (news, tables, this playbook), not chat.
- **honest-edges** — limitations stated where users read them (`README ## Honest edges`).
- **human-gated-irreversible** — network sync opens a PR; merges/publishes stay human.
- **the repo audits itself** — `data/ainative.yml` + `scripts/ainative.py` score HOW the repo
  operates with in-repo evidence, gated in CI (a discipline regression fails the build).

## 3. The build loop (goal-10x)

Research (map, don't guess; read backbone + sibling repos) → Absorb (reflect intent ≤6 lines) →
Coach (≤2 forks) → **Drive to green** (verification is the only truth; drive the *discovered*
check) → Self-improve (bank the lesson into `data/`, not chat). The ROADMAP is a machine-checkable
milestone table; each milestone has a runnable DoD. **Score with `anyagent analyze <dir>` at EACH
milestone**, not once at the end — and don't game a sub-metric (trust the artifact, not the label).

## 4. Signature files often forgotten — add them

`data/ainative.yml` + `scripts/ainative.py` + test (self-audit, CI-gated ≥90) · `data/news.yml`
→ drift-gated README block · `eval/<skill>.md` (should / should-not-trigger, each backed by a
test) · `llms.txt` · `.github/ISSUE_TEMPLATE/gate-dispute.md` · `## Honest edges` in README.

### 4a. Agentic webapp? Then 1-click activation is part of DONE

Paul's standing rule (2026-08-01): if the repo has a demo/webapp, its link goes at the
**top of README** (first screen), the server **auto-opens the browser** on start
(`--no-open` escape hatch for CI), and the app is installable (PWA manifest / one
`make demo` command). Add a drift test that pins the README link — undemoed ⇒ unshipped.
**Amendment (2026-08-01):** 1-click means **remotely visitable** — deploy a public
demo (Vercel) serving a build-time snapshot that NEVER executes; receipts replace
execution panels remotely; the local command stays the power path.

## 5. Transferable lessons (earned, promote-worthy)

1. **The satellite pattern is domain-agnostic** — if your repo composes external repos, index +
   pinned digest + generated skill, never a fork.
2. **The gate's semantics are domain-specific; the gate discipline is universal** — build the gate
   that encodes YOUR domain's "verified" (geometry / claim / manifest).
3. **Model orchestration as a graph and gate reachability** — no orphan node; no path reaches the
   output bypassing the gate (networkx).
4. **Make the closed loop a real object** — generate → score vs an independent referee → refine,
   roll back regressions, report how it converged (F→A).
5. **Benchmarks/evals are first-class modules with honest "not measured."**
6. **Keep the gate offline & deterministic**; put all network in `sync` + a weekly workflow (use a
   FakeProvider/fixtures for reproducibility).
7. **Digest a cited repo with a parallel sub-agent** that pins the HEAD sha and flags unconfirmed
   facts (never invent an install command or API signature).
8. **An evidence-type taxonomy defeats "engagement is not evidence"** — tag every finding; weak
   evidence can't rank until it crosses an adoption window.
9. **Encode architectural invariants as executable tests** (import-lint for dependency direction,
   schema-enforced provenance, graph-integrity) — structural gates catch the real bugs.
10. **Greenfield doc phases** — `anyagent goal` can't route a document phase; build the finish line
    first (a manifest gate: file exists + min words + required headings), then drive docs to green.
    Human approval lives in a doc's `Status:` line the gate relays verbatim, never infers.
11. **Compile the marketing adjectives into gates** (GodView-anything, 2026-07-26) — when the goal
    says "most comprehensive / most up-to-date / most in-depth", recompile each adjective into a
    machine check (a north-star coverage metric · measured STALE flags · a digest-required
    inclusion rule). The README then claims only what the gates prove — marketing and honesty stop
    being in tension.
12. **The gate's first conviction is usually its author** — self-referential numbers in prose
    (counts, scores, "N satellites") drift the moment they're typed; generate them from the
    machine report or cross-check before committing (GodView's birth commit claimed 31 satellites;
    the metric said 30). Corollary: a validator that has never fired on YOU is probably not
    checking anything.
16. **For a values-laden or person-facing corpus, make the ethical boundary the STRICTEST machine
    gate** (GodView agentic-ministries, 2026-07-27). When a spec points the engine at something that
    touches real people or sacred/contested ground (here: spiritual care, prophecy), the 10x is to
    turn the *restraint* into executable checks, not prose promises: a BoundaryGate on every card
    (what it points back to + what it must never do + measured_by return_sharper, never engagement);
    exactly ONE committed action (a list is survey-mode — reject it); a `no_diagnosis` denylist on
    the person-facing office; resonance capped so a current event can never be stated as fulfilled;
    and the contested framework itself recorded as *contested*, adjudicated nowhere. Register the
    domain's external infrastructure (scripture/lexicon MCPs) as satellites — "don't rebuild what
    exists" is both good engineering and the spec's own rule. And when a NEW spec re-implements your
    existing core, realize it ON the engine as spec-as-data, never as a parallel schema tree
    (maker-is-not-checker + spec-as-data). Honor the spec's own STOP line (no person-contacting).
15. **A truth-discipline engine is corpus-agnostic — prove it on a second, harder corpus** (GodView,
    2026-07-26). Once you have an evidence-tiered engine (ladder + provenance + graph + corrections +
    dual-render + gates), the mechanism doesn't care what the corpus is. Pointing it at a
    hype-prone, provenance-loose domain (here: biblical prophecy / redemptive history) is not a
    stretch — it's where the discipline is needed *most*, and the right move is to turn the
    discipline UP, not down. Concretely: (a) make confidence run *opposite* to emotional pull (the
    thing people are surest of is often the weakest-evidenced); (b) add domain-specific gates that
    encode the field's known failure modes as machine checks (no-date-setting, resonance-can't-be-
    stated-as-fact, a required falsifier per claim — Popper as a schema field); (c) keep the
    strongest counter-case *in* the card (a prophecy's predictiveness hinges on its dating debate —
    surface it, don't bury it); (d) treat the domain's famous failures as a *dataset* of ⚪
    corrections, not an embarrassment; (e) give the new corpus its OWN metric so it never inflates
    the original one. Handle a values-laden domain by tiering the checkable (archaeology, textual
    transmission) separately from the interpretive and the faith claim — label the epistemic class,
    adjudicate none. See `KNOWLEDGE_PLAYBOOK.md` + a domain SPEC.
14. **Ingest a big catalogue module-by-module, and guard against mis-attribution** (GodView,
    2026-07-26). When a note dumps ~130 items that blend the subject repo's real stack with a broad
    adjacent-tech catalogue, don't blast it in one pass: write a SPEC with a domain taxonomy, deliver
    one fully-verified module (satellites verified via the GitHub API, cards tiered + provenanced),
    keep the gate green, and QUEUE the rest honestly. The load-bearing rule is *no mis-attribution* —
    a technique belongs to a repo only if verified THERE; everything else is its own satellite. And
    when the ask says "validate against principles X/Y/Z", make each an executable gate as
    spec-as-data (a principle with no gate is a slogan) — cite a sibling repo as canonical rather
    than re-defining it (graph-engineering-anything, loop-engineering-anything). A graph-engineering
    gate that actually checks reachability (no orphan card) is worth more than one that just asserts
    "we use a graph".
13. **A source note is a hypothesis set — verify at each claim's native altitude** (GodView, 2026-07-26).
    Ingesting third-party commentary (a video, a blog) into a knowledge base? Tier every claim by the
    evidence you can actually get: read the CODE for a code claim, the PAPER for a math claim, the
    PRICING PAGE for a price. A verified ladder (verified-in-code / corroborated / claimed / disputed)
    enforced by a gate turns "digest this" into trustworthy knowledge. The most valuable output is the
    **disputed** cards — the note said "$9/mo", the page says $39.99; the note said "LLM gated on
    critical events", the code says premium-entitlement gating. A correction kept is worth more than a
    claim repeated. Quarantine by source type (commentary enters low), promote by evidence (an
    artifact_ref, not the narrator's confidence). Dual-render one spec to a human doc and an agent
    surface — never maintain two. See `KNOWLEDGE_PLAYBOOK.md` (new canonical, this date).

## 6. Minting the next repo

`./new-project.sh <name> …` seeds this playbook + the shape's CLAUDE.md. Then: compile `GOAL.md`,
stand up `data/*.yml` + `make check` FIRST (green at birth), add the flagship skill, then
satellites one repo at a time (candidate → digested → integrated, each advance gated by on-disk
evidence). Wire `data/ainative.yml` early so the repo holds its own discipline from day one.


## UI disclosure discipline (Paul's rule, 2026-08-02 — from the publish kit)

A tool that operates ON an object the user is already looking at opens INLINE at that
object — collapsed by default, one click to expand, zero navigation — never as a separate
page or tab. Separate pages are for separate OBJECTS: a cross-object dashboard earns a
route; a per-object action (a share kit on an article card, an approve button on a claim,
a detail view on a row) earns a disclosure. Two corollaries: (1) when the disclosure's
data is missing, SAY the gap inline ("no promo kit yet — author content/promos/<slug>.yml")
rather than silently falling back; (2) pin the pattern with a source test so the separate
page can't quietly come back. Origin story: the portfolio's publish kit shipped as a
standalone HTML page and had to be folded into the article card's own button — build it
inline the first time.
