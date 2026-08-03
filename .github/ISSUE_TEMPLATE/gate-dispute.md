---
name: Gate dispute
about: Challenge a control mapping, an evidence tier, a status promotion, or a gate verdict
title: "[dispute] "
labels: dispute
---

## What are you disputing?

- [ ] A **control mapping** (`covers:` in `data/registry.yml` or `data/knowledge.yml`)
- [ ] An **evidence tier** (`verified` / `corroborated` / `claimed` / `disputed`)
- [ ] A **status** on the ladder (⚪ candidate / 🟡 digested / 🟢 integrated)
- [ ] A **gate verdict** (an exit code or a NOT_MEASURED)
- [ ] Something else

## The specific claim

> Quote the exact line from `data/*.yml`, a digest, or a generated table.

**id:**
**file:line:**

## Why it is wrong

Control mappings are **authored by us** (`mappings_asserted_by: secure-anything`) and are a
judgement call, not the upstream project's claim. Evidence tiers are capped by what was actually
read. Both are meant to be disputable — that is why this template exists.

## The evidence

What should we read? A primary source beats a summary; a run receipt beats a mapping.

- [ ] I have a **primary source URL** (would support upgrading a tier)
- [ ] I have a **run receipt / reproduction** (would support a status change)
- [ ] I am reporting that a claim **cannot be verified** (would support downgrading to `disputed`)

## Proposed change

What should `data/` say instead? Remember: a correction retained is worth more than a claim
repeated — a downgrade to `disputed` is a legitimate and valuable outcome.
