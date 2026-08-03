# eval — /secure-anything routing

Every row here is a **pytest case** (`tests/test_router_eval.py` parses this file). A routing
claim that isn't in this table isn't a claim we make. The refusals matter as much as the hits:
a router that never says "I don't have that" is guessing.

Expectation syntax:

| token | meaning |
|---|---|
| `capability:<id>` | that capability must be the TOP match |
| `capability?<id>` | that capability must appear somewhere in the matches |
| `card:<id>` | that knowledge card must appear in the matches |
| `warn:<id>` | routing must emit a warning naming that id |
| `gap` | nothing may match — the router must bank the gap instead of guessing |

## Should route — capabilities

| intent | expect | why |
|---|---|---|
| `scan my repo for vulnerabilities` | capability:codex-security | the repo Paul named; whole-repo AppSec scan |
| `I need static analysis that runs offline` | capability?semgrep | offline + deterministic is semgrep's niche |
| `red team my llm before launch` | capability?garak | probe sweep is garak's job |
| `benchmark prompt injection defences` | capability?agentdojo | the defence-side benchmark |
| `review this pr` | capability:agentgate | our own organ owns the PR boundary |
| `anchor the ledger so an auditor believes us` | capability:rekor | external transparency log |
| `gate an mcp server` | capability?mcp-spec | the tool boundary ASI02/ASI07 describe |
| `threat model my agent` | capability?agent-wiz | map the agent before gating it |
| `npx skills` | capability?skills-registry | the skill supply chain is infrastructure to gate, not a defence |

## Should route — knowledge

| intent | expect | why |
|---|---|---|
| `what is the lethal trifecta` | card:lethal-trifecta | the core triage model |
| `why is detection not enough` | card:camel-control-flow-integrity | architecture beats classification |
| `how should i architect my agent` | card:paper-design-patterns | six concrete patterns |
| `what should i read` | card:book-developers-playbook-llm-security | the practitioner book |
| `who is wunderwuzzi` | card:person-johann-rehberger | canonical for PoC-first offensive work |
| `eu ai act article 12` | card:std-eu-ai-act-art12 | the record-keeping obligation |
| `is this catch rate real` | card:paper-strongreject | strict scoring, no inflation |

## Should warn — the refusals

| intent | expect | why |
|---|---|---|
| `llamafirewall` | warn:purplellama | license NOASSERTION ⇒ pointer only, never vendored or run in our CI |
| `nemo guardrails` | warn:nemo-guardrails | same license wall |
| `how good is codex security` | warn:claimed-codex-security-catch-rate | a vendor number must never be relayed as a fact |
| `is this skill safe` | warn:skills-audit-coverage-gap | skills.sh audits 50 skills and publishes no methodology — say so, don't imply audited=safe |
| `brace framework` | card:disputed-brace-framework | kept as a correction: unverifiable, do not use in messaging |

## Should bank a gap — no guessing

| intent | expect | why |
|---|---|---|
| `book me a flight to tokyo` | gap | not a security intent; the router must not invent a match |
| `write me a poem about firewalls` | gap | out of domain |
| `formally verify my rust borrow checker proofs` | gap | a real gap worth banking — no capability covers formal methods |
