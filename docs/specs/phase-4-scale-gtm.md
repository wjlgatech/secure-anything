# SPEC — Phase 4: Scale & GTM  (Status: ⬜ Planned)

## Goal
Make it multi-tenant, hardened, and sold: pilots with teams running 10–50 coding agents
daily, and a validated pricing model.

## User stories
- As an org admin, I onboard my org with isolated data, RBAC, and my own secret storage.
- As a buyer, pricing maps to value I understand (seats / gated actions / compliance tier).

## In scope
1. **Multi-tenancy**: org isolation, RBAC, per-org KMS for secrets.
2. **Hardening**: SOC2-track controls, HA workers, rate limiting, backpressure, DR for the
   ledger.
3. **Pilots**: 2–3 design partners; instrument activation + retention (does the pain drop?).
4. **Pricing**: test per-seat vs. per-gated-action vs. compliance tier.

## Out of scope
New product surfaces beyond P3 unless a pilot demands one.

## Task checklist
- [ ] Tenancy model + RBAC + per-org KMS.
- [ ] HA workers, rate limiting, ledger backup/restore + verify-on-restore.
- [ ] SOC2 control mapping (reuse the audit ledger as evidence).
- [ ] Pilot onboarding + usage instrumentation.
- [ ] Pricing experiment with real prospects.

## Definition of Done
A design-partner pilot is live in an isolated tenant, retention instrumented, and the
buyer + pricing hypothesis validated with real prospects (see open questions in
[../01-MARKET.md](../01-MARKET.md)).

## Risks / open questions
- Buyer identity (platform eng vs CISO vs compliance) still unproven — validate before spend.
- Build-vs-buy pressure (a team could roll a GitHub Action); moat = audit/compliance +
  cross-agent horizontal + approval UX.
