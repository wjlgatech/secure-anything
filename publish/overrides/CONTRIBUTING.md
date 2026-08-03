# Contributing

The most valuable thing you can send is **evidence**, not code. This repo's whole claim is that
every statement in it is backed by something checkable — so a contribution that upgrades, dates,
or *refutes* a claim is worth more than a feature.

## The one rule

**`make check` must pass.** It is the canonical gate and CI runs exactly it — ruff, the charter
manifest, registry evidence, generated-surface drift, the self-audit (≥90), and pytest.

**Never weaken a test, a budget, or an evidence tier to make something pass.** If a gate blocks
you, either do the work it is asking for or open an issue arguing the gate is wrong. An honest ❌
beats a fake ✅, and that is not a slogan here — it is what the repo measures.

```bash
make install && make check
```

## High-value contributions, roughly in order

1. **Promote a ⚪ candidate to 🟡 digested.** Write `docs/satellites/<id>.md` with facts read
   **at a pinned SHA**, and add `pinned_sha` to `data/registry.yml`. Label anything you could not
   directly verify as `UNCONFIRMED` — that label is a feature, not an admission.
2. **Dispute a control mapping.** The `covers:` fields are our editorial judgement. If
   `garak` does not really cover `LLM07`, say so via the
   [gate-dispute template](.github/ISSUE_TEMPLATE/gate-dispute.md).
3. **Upgrade or downgrade an evidence tier.** Found the primary source for a `corroborated`
   card? Upgrade it. Found that a `verified` claim does not hold? **Downgrade it** — a
   correction retained is worth more than a claim repeated.
4. **Add a missing capability or knowledge card.** One entry in `data/registry.yml` or
   `data/knowledge.yml`. If adding it costs more than that, tell us — the composition layer has
   leaked and that is a bug.
5. **Close a coverage gap.** `make northstar` prints controls with *no* capability at all. Those
   are honest holes in the field, not just in this repo.

## Non-negotiables for data

- **Verify, never recall.** Every external fact (star count, licence, SHA, arXiv id, title) is
  read from an API or the primary source and stamped with `verified_at`. If you did not read it,
  tier it `claimed` and add an `unconfirmed:` note. We have already been burned once: the
  registry lists `microsoft/PyRIT` because `Azure/PyRIT` turned out to be archived.
- **Unresolved licence ⇒ pointer only.** `NOASSERTION` is treated as restrictive: never vendored,
  never executed in CI, never marked integrated.
- **Never vendor a satellite.** Pointer + pinned SHA + digest, or nothing.
- **Never hand-edit a generated block.** Change `data/`, run `make build`.

## What is and is not here

This is the **composition layer**: the registry, router, gate seam, ledger and north star, in
full and under Apache-2.0. It is genuinely usable on its own — write ~200 lines of adapter and
your tool becomes a gateable capability.

The reference **organ** built on it (an actor-aware PR firewall) is developed privately and
appears in the registry as a pointer. It contributes **zero** to the north star here, because it
has no public run receipt — the same bar every external capability is held to. We would rather
be transparent about that boundary than blur it: nothing in this repo depends on code you cannot
read.

## Scope

Defensive use only. Red-team capabilities are indexed for evaluating **systems you own or are
authorised to test**. Contributions that add exploit payloads, target third parties, or aid
evasion will be declined.
