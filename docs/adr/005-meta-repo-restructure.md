# ADR-005 — AgentGate becomes secure-anything, a meta-repo; AgentGate becomes its first organ

- **Status:** Accepted
- **Date:** 2026-08-03
- **Playbook:** `docs/META_REPO_PLAYBOOK.md` (charter-first), on `docs/REPO_PLAYBOOK.md` (mechanics)

## Context

AgentGate solved one problem well — a PR firewall with an actor-aware policy and a hash-chained,
signed audit ledger. But the ecosystem it lives in is large and moving fast: scanners
(codex-security, semgrep), guardrails (LlamaFirewall, NeMo, llm-guard), red-team kits (garak,
promptfoo, PyRIT), benchmarks (AgentDojo, ASB), provenance infrastructure (Sigstore/Rekor),
control frameworks (OWASP LLM & Agentic Top 10, MITRE ATLAS, NIST AI RMF), plus a literature and a
set of people and labs that a serious gate should be able to cite.

Absorbing any of that into AgentGate would have made a single product slowly become a bad version
of twenty other tools. The direction requested was explicit: **keep the core lean, make the
ecosystem rich.**

## Decision

1. **The repo becomes `secure-anything`, a meta-repo.** It owns no domain logic. Its product is a
   verified composition: a registry, a deterministic router, a uniform gate seam, a tamper-evident
   ledger, and a computable north star.
2. **AgentGate becomes the first organ** at `src/secure_anything/organs/agentgate/`. It keeps its
   own README, its own roadmap (Phases 0–4 unchanged), and all of its tests. Nothing was deleted.
3. **The ledger moves INTO the core** (`secure_anything.ledger` + `secure_anything.store`). The
   record must outlive any single organ — that record is the moat, not the PR firewall.
4. **Leanness is a budget with a test.** `test_core_is_lean` fails the build above 600 LOC;
   `test_core_never_imports_an_organ` and `test_core_names_no_vendor_or_protocol` enforce the
   dependency direction and the absence of domain knowledge. The budget fired on its very first
   run (605 LOC) and was met by cutting code, not by raising the number.
5. **Richness is a coverage metric, not a count.** The north star (Verified Control Coverage)
   counts only capabilities that ran *here* and left a receipt. Adding a registry entry moves it
   by zero.
6. **Privacy: stays PRIVATE.** Declared in `docs/VISION.md` on day one. No publishing machinery in
   the repo; satellites carry a `visibility:` field so a future flip leaks nothing.

## Alternatives considered

- **Mint a fresh `secure-anything` and leave `agentgate` alone.** Cleanest doctrinal separation,
  but splits attention across two private repos and abandons the rename that was asked for.
- **Rename and keep the PR-firewall code as first-class core modules.** Smallest diff, but the
  core would carry GitHub-webhook logic forever — the exact failure mode the meta-repo playbook
  names ("the moment a meta-repo implements a domain inline, it has failed").

## Consequences

- **Positive:** one YAML entry = one new capability. Adding a satellite costs a registry row plus a
  digest, never core code.
- **Positive:** AgentGate is now held to the same promotion bar as any external tool — it sits at
  🟡 digested, not 🟢, because it has no run receipt through the gate seam yet. We do not exempt
  ourselves.
- **Negative:** import paths changed for every consumer (`agentgate.*` →
  `secure_anything.organs.agentgate.*`). Contained, and the move surfaced a real fail-open bug
  ([ADR-004](004-fail-closed-policy-fallback.md)) that had been latent.
- **Negative:** VCC reads 0% at birth. That is accurate and deliberate — the number is the queue.
