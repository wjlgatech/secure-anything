# Organ digest — `agentgate`

> **Status: 🟡 digested.** An organ, not a satellite: it lives in this repo under
> `src/secure_anything/organs/agentgate/`. Digested rather than integrated because it has not yet
> produced a run receipt **through the core gate seam** — the same bar every external capability
> must clear. We do not exempt ourselves.

| field | value |
|---|---|
| location | `src/secure_anything/organs/agentgate/` |
| kind | organ (ours) |
| role | gate |
| license | Proprietary — All Rights Reserved (confirmed) |
| visibility | private |
| verified_at | 2026-08-03 |
| covers | LLM01, LLM02, LLM03, LLM06, ASI02, ASI03, ASI04, ASI09 |

## What it does

An **actor-aware PR firewall**: verify webhook HMAC → classify the author (human · ai_agent · bot)
→ run deterministic offline checks (secret scan · protected paths · diff size · optional
agent-audit SAST) → optional LLM review → an actor-aware decision → append to a hash-chained,
Ed25519-signed audit ledger. Agents are held to a stricter bar than humans, and the difference
lives entirely in `policy/default_policy.yaml` — data, not prompt.

Full documentation: [`docs/organs/agentgate/README.md`](../organs/agentgate/README.md) ·
Roadmap (Phases 0–4): [`docs/organs/agentgate/ROADMAP.md`](../organs/agentgate/ROADMAP.md)

## Verified evidence on disk

- **Tests:** the organ's suite runs inside `make check`, offline and deterministic — no network,
  no API key. Phase 0 and Phase 1 are code-complete and offline-verified.
- **Ledger:** now **core-owned** (`secure_anything.ledger` + `secure_anything.store`), because the
  record must outlive any single organ. Chain integrity and Ed25519 signature tests live in
  `tests/test_ledger_chain.py` and `tests/test_ledger_signing.py`.
- **ADR-003** records the Ed25519 signing decision; **ADR-004** records the fail-closed policy
  fallback found during the 2026-08-03 restructure.

## Promotion path to 🟢

Wrap `evaluate()` behind a `GateAdapter` and run it against a fixture PR through
`secure_anything.gate`, writing `exit_code` + decision evidence into `runs/agentgate/`. That single
receipt would take VCC from 0/20 to 8/20 — which is exactly why the receipt, and not the mapping,
is what counts.

## Honest edges (carried from the organ's own docs)

- **Branch protection is Actions-bypassable.** If an attacker can bypass branch protection they can
  bypass the gate. Productising and verifying GitHub Rulesets is Phase 1.5 and is unfinished.
- **Actor classification is login-substring based** (`actor.py`) and therefore spoofable; moving to
  GitHub App attribution / OIDC is open work.
- **The ledger is tamper-evident, not tamper-proof.** See the root README's Honest edges and the
  `rekor` registry entry, which exists specifically to close this gap.
- **Live-repo E2E is still pending credentials.** Everything is verified offline; the live loop is
  not yet demonstrated end to end.
