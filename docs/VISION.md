# VISION — secure-anything

> The charter. Written before the scaffold, gated like code (`scripts/manifest_gate.py`).
> Governs: why this repo exists, what it will never do, and the one number that says whether
> it is winning. Extends `docs/META_REPO_PLAYBOOK.md`.

**Privacy: PRIVATE.** Declared day one (2026-08-03). No publishing machinery lives in this repo —
a publish flow inside a must-stay-private repo invites accidental exposure. Satellites carry a
`visibility:` field so a future public flip leaks no internal detail, but the flip is not planned
and is not a milestone.

---

## Vision

Every consequential action taken by an AI agent — merging code, moving money, calling a tool,
touching production — passes a gate that a machine can re-run and an auditor can re-verify years
later. Security for agents stops being a vendor's claim and becomes an **exit code plus a signed
receipt**.

## Mission

secure-anything is the **composition layer** for agent security: one registry of every capability
worth trusting (external tools, family organs), one deterministic router from a messy intent to
the right capability, one uniform gate seam that turns any of them into a comparable exit code,
and one tamper-evident ledger that records every run. It owns **no domain logic** — it composes,
verifies, and remembers.

The core stays lean on purpose. The ecosystem is where the value compounds.

---

## North-star metric

**Verified Control Coverage (VCC)** — the share of in-scope security controls that are covered by
at least one **🟢 integrated** capability whose gate has actually run *here* with a recorded exit
code and an on-disk receipt.

```
VCC = |controls with >=1 integrated capability holding a run receipt| / |controls in scope|
```

- **In scope** = the control set in `data/controls.yml` (OWASP Top 10 for LLM Apps + OWASP Top 10
  for Agentic Applications, at minimum).
- Computed offline by `python3 scripts/northstar.py`. No network, no judgement call.
- **Ungameable by hoarding**: naming a satellite (⚪) moves VCC by zero. Pinning a digest (🟡)
  moves VCC by zero. Only a capability that *ran here and produced a receipt* counts.
- A milestone that ships mechanics without moving VCC is logged as **maintenance, not progress**.

Supporting metrics (reported, never confused with the north star): satellites by status,
knowledge cards by evidence tier, measured STALE count.

---

## Operating modes

| Mode | What it means | Unlocked |
|---|---|---|
| **AI-assisted** — human leads, AI supports | Every gate is run by, or on behalf of, a human who reads the result. Irreversible steps (merge, publish, rename, key rotation) stay human. | Now (M0) |
| **AI-autonomous** — bounded workflows, validation gates, human oversight | An agent may run a *named, bounded* chain end-to-end (e.g. scan → gate → ledger) without a human in the middle, because every step is offline-deterministic, every result is an exit code, and every run is signed into the ledger. Still human-gated at every irreversible step. | M4 (Autonomy), and only for chains with a recorded golden example |

---

## Non-goals

Stated here because users read charters, and because a non-goal that lives only in someone's head
is not a boundary.

1. **Not a scanner.** secure-anything does not implement vulnerability detection, prompt-injection
   classification, or static analysis. If a capability is missing, the answer is a satellite or an
   organ — never inline domain logic. (Meta law: the moment a meta-repo implements a domain
   inline, it has failed.)
2. **Not a vendor of trust claims.** It aggregates **exit codes**, never claims. "No evidence" is
   reported as *not measured* and excluded — it never becomes a pass.
3. **Not a fork farm.** No external repo is vendored. Pointer + pinned SHA + digest, or nothing.
   AGPL and unlicensed upstreams are pointer-only and run upstream.
4. **Not an offensive-security toolkit.** Red-team satellites are indexed for *defensive
   evaluation of your own systems*. No exploit distribution, no capability aimed at third parties.
5. **Not a certification.** A green gate is evidence, not an audit opinion, not a permit, not a
   SOC 2 report, and not legal advice about the EU AI Act.
6. **Not a replacement for AgentGate.** The PR firewall keeps shipping — as this repo's first
   organ, with its own roadmap and its own tests.

---

## Honest edges

- VCC is low at birth and is *supposed* to be. The number is the work queue.
- Control mappings (which satellite covers which OWASP item) are authored by us and are a
  judgement call; each mapping records who asserted it and when, and is disputable via
  `.github/ISSUE_TEMPLATE/gate-dispute.md`.
- A hash-chained, Ed25519-signed ledger is tamper-evident **against everyone but the operator who
  holds the key and the database**. External anchoring (WORM / RFC3161 / Rekor) is unbuilt; until
  it lands, this repo does not use the word "tamper-proof".
- Satellite freshness is *measured* (a STALE flag against the pinned SHA), never promised.
