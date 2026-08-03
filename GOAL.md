# GOAL — secure-anything

The founding intent, verbatim, recompiled into a machine-verifiable contract (10xgoal
discipline). This file is the contract; `make check` is the proof.

---

## 1. Verbatim intent (Paul Wu, 2026-08-03)

> use our playbook (which one?) to rename and expand agentgate to secure-anything, a meta-repo
> with super-tool (i.e. "/secure-anything"). for example, include and integrate repo like this
> one: https://github.com/openai/codex-security. There are other top rated repo, skills, books,
> blogs, research papers, research labs, individuals need to be include and integrated. NO rush,
> research, plan and execute with test & validation gates.

> keep the core (ai native infra) really lean, make the eco really rich (tooling,
> knowledge-base, <you-name-others>)

**Answered in-band:** the playbook is `docs/META_REPO_PLAYBOOK.md` (charter-first, composition
doctrine, milestone arc), layered on `docs/REPO_PLAYBOOK.md` for mechanics.

---

## 2. Eval of the intent as stated

| Clause | Verdict | Why |
|---|---|---|
| "rename agentgate to secure-anything" | ✅ strong | Binary, verifiable: repo name, package name, import path. |
| "a meta-repo with super-tool" | ✅ strong | The playbook defines meta-repo precisely (registry + router + chains, no domain logic). |
| "include and integrate repo like codex-security" | ⚠️ **bundled** | *Include* and *integrate* are two different gates. Splitting them is the whole status ladder. |
| "other top rated repo, skills, books, blogs, research papers, research labs, individuals" | ⚠️ **unmeasurable as written** | "Top rated" by what? How many is done? Needs a coverage target and an evidence tier. |
| "keep the core really lean" | ⚠️ **unmeasurable as written** | Lean by what number? Needs a hard budget with a test. |
| "make the eco really rich" | ⚠️ **unmeasurable as written** | Rich by what number? "Count of things" is gameable — needs to be tied to proof. |
| "execute with test & validation gates" | ✅ strong | `make check` exit 0 is the finish line. |

## 3. The un-bundling — seven machine-verifiable goals

| # | Goal | Machine check | Status |
|---|---|---|---|
| G1 | The repo IS secure-anything | `gh repo view --json name` = `secure-anything`; `import secure_anything` works; no `agentgate` import path outside `organs/` | ⬜ |
| G2 | The core is **lean**, by budget | `test_core_is_lean`: core (`src/secure_anything/*.py`, excluding `organs/`) ≤ **600 LOC** and imports nothing from `organs/` (import-lint) | ⬜ |
| G3 | The core owns **no domain logic** | `test_no_domain_logic_in_core`: no core module names a vendor, a protocol, or a scanner (`github`, `semgrep`, `webhook`, …) | ⬜ |
| G4 | "Include" is a real, separable gate | Every registry entry is ⚪/🟡/🟢; a validator **refuses** a 🟡 without `docs/satellites/<id>.md` + `pinned_sha`, and a 🟢 without a run receipt | ⬜ |
| G5 | The eco is **rich**, by coverage not count | ≥ **40** ecosystem entries across ≥ **6** classes (tool · knowledge · person · lab · standard · skill-library), each with `verified_at` and an evidence tier; **zero** unverified factual claims | ⬜ |
| G6 | The eco is **proven**, not hoarded | North star **VCC > 0** with ≥1 chain walkthrough carrying verbatim exit codes | ⬜ |
| G7 | The super-tool routes deterministically | `/secure-anything` SKILL.md is **generated** from `data/` (drift-gated) and every routing case in `eval/secure-anything.md` — including the refusals — is a passing pytest | ⬜ |

**"Really lean" is now 600 LOC with a test. "Really rich" is now 40 entries × 6 classes × zero
unverified claims. Neither is a vibe any more.**

## 4. The 10x move

Not "collect more security tools" — an awesome-list does that for free and rots in a month.

The 10x is that **every entry in the ecosystem is reachable through one deterministic router and
reducible to one comparable exit code, and every run is signed into a ledger that outlives the
tool that produced it.** Tools churn; the record of what was checked, by what, on what date,
against which control — that compounds. The ecosystem is the surface; the ledger is the moat.

## 5. Definition of done for M0

`make check` exits 0 with: ruff clean · all pre-existing AgentGate tests still green · the new
core/registry/router/ledger tests green · charter manifest gate green · build drift-check green ·
self-audit ≥ 90 · every eval routing case a passing test.
