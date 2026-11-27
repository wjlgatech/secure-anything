#!/usr/bin/env python3
"""Generate every published surface from data/*.yml — and prove it hasn't drifted.

`python3 scripts/build.py`          writes the generated files
`python3 scripts/build.py --check`  exits 1 if anything on disk differs from what data/ implies

Spec-as-data means the README tables and the flagship SKILL.md are OUTPUT, never source.
Hand-editing a generated block is a build failure, not a style preference.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from secure_anything.coverage import compute, receipts_on_disk  # noqa: E402
from secure_anything.spec import Spec, Status, load_spec  # noqa: E402

SKILL = ROOT / "skills" / "secure-anything" / "SKILL.md"
README = ROOT / "README.md"

ROLE_ORDER = [
    ("gate", "Gate (ours)"), ("scanner", "Scanners"), ("guardrail", "Guardrails (runtime)"),
    ("redteam", "Red team"), ("benchmark", "Benchmarks"), ("policy", "Policy engines"),
    ("threat-model", "Threat modelling"), ("provenance", "Provenance & supply chain"),
    ("skill-library", "Skill supply chain"), ("standard-impl", "Protocols"),
    ("secrets", "Secrets management"), ("compliance", "Compliance automation"),
    ("engine", "Engines"),
]
CARD_ORDER = [
    ("concept", "Concepts"), ("paper", "Papers"), ("book", "Books"), ("blog", "Blogs"),
    ("person", "People"), ("lab", "Labs"), ("standard", "Standards"),
    ("skill-library", "Skill libraries"),
]


def _rows(s: Spec) -> str:
    out = []
    for role, label in ROLE_ORDER:
        caps = [c for c in s.capabilities if c.role == role]
        if not caps:
            continue
        out.append(f"\n**{label}**\n")
        out.append("| | id | what it does | license | covers |")
        out.append("|---|---|---|---|---|")
        for c in sorted(caps, key=lambda x: (-x.status.rank, x.id)):
            lic = c.license or "—"
            if c.pointer_only and c.kind == "external":
                lic += " ⚠️ pointer-only"
            covers = ", ".join(c.covers) or "—"
            out.append(
                f"| {c.status.mark} | [`{c.id}`]({c.url}) | {c.capability} | {lic} | {covers} |"
            )
    return "\n".join(out)


def _cards(s: Spec) -> str:
    tier = {"verified": "✅", "corroborated": "🟢", "claimed": "🟠", "disputed": "🔴"}
    out = []
    for kind, label in CARD_ORDER:
        cards = [c for c in s.cards if c.kind == kind]
        if not cards:
            continue
        out.append(f"\n**{label}**\n")
        out.append("| evidence | what | by | why it matters |")
        out.append("|---|---|---|---|")
        for c in sorted(cards, key=lambda x: x.id):
            why = (c.why_it_matters or c.summary or c.canonical_for).strip().replace("\n", " ")
            why = re.sub(r"\s+", " ", why)
            why = why[:150] + ("…" if len(why) > 150 else "")
            link = f"[{c.title}]({c.url})" if c.url.startswith("http") else c.title
            out.append(
                f"| {tier[c.evidence.value]} {c.evidence.value} | {link} | "
                f"{c.by or '—'} | {why} |"
            )
    return "\n".join(out)


def _northstar(s: Spec) -> str:
    cov = compute(s, receipts=receipts_on_disk())
    by_status = {st: sum(1 for c in s.capabilities if c.status is st) for st in Status}
    tiers = {}
    for c in s.cards:
        tiers[c.evidence.value] = tiers.get(c.evidence.value, 0) + 1
    return "\n".join([
        f"**Verified Control Coverage (VCC): {len(cov.covered)}/{cov.total} "
        f"= {cov.vcc:.1%}**  ← the north star",
        "",
        f"- Capabilities: {by_status[Status.INTEGRATED]} 🟢 integrated · "
        f"{by_status[Status.DIGESTED]} 🟡 digested · {by_status[Status.CANDIDATE]} ⚪ candidate",
        "- Knowledge cards: " + " · ".join(f"{v} {k}" for k, v in sorted(tiers.items())),
        f"- {len(cov.claimed_only)} control(s) are **mapped** to a capability but have no run "
        "receipt. Mapped is not measured — they count as zero.",
    ])


def render_skill(s: Spec) -> str:
    caps = [c for c in s.capabilities if c.triggers]
    return f"""---
name: secure-anything
description: >-
  The super-tool for agent security. Routes any security intent — scan a repo, red-team an
  agent, pick a guardrail, cite a control, find the paper or the person — to the right
  capability or knowledge card, with the licence wall and the evidence tier attached.
  Trigger: "/secure-anything", or any intent about securing an agent, an LLM app, or the
  code an agent writes.
---

<!-- GENERATED FROM data/registry.yml + data/knowledge.yml by scripts/build.py. DO NOT EDIT. -->

# /secure-anything

One front door for agent security. This skill **owns no domain logic** — it routes.

## How to use it

1. Take the user's intent verbatim.
2. Run the deterministic router (never guess):

   ```bash
   make route Q="<their intent>"
   ```

3. Relay **every** warning verbatim. They are not decoration:
   - a **licence wall** (`pointer-only`) means run it upstream — never vendor it,
     never run it in CI;
   - an **evidence tier** below `verified` means do not restate the number as a fact.
4. If the router banks a **gap**, say so plainly and record it. Do not substitute a near miss.

## The status ladder — what a mark means

| mark | meaning | counts toward the north star? |
|---|---|---|
| ⚪ candidate | named, metadata verified | **no** |
| 🟡 digested | pinned SHA + digest on disk | **no** |
| 🟢 integrated | its gate ran HERE, exit code recorded in `runs/` | **yes** |

## Capabilities ({len(caps)} routable)

{_rows(s)}

## Knowledge base ({len(s.cards)} cards)

{_cards(s)}

## Refusals this skill must make

- **Unconfirmed licence** → pointer only. Do not vendor, do not execute in our CI.
- **`claimed` evidence** → never relay the number as a fact; name the tier.
- **No match** → bank the gap. A router that always finds something is guessing.
- **Unmeasured item in a blocking gate** → the gate is RED. No evidence means no.
"""


def render_readme_blocks(s: Spec) -> dict[str, str]:
    return {"capabilities": _rows(s), "knowledge": _cards(s), "northstar": _northstar(s)}


def splice(text: str, name: str, body: str) -> str:
    begin, end = f"<!-- BEGIN GENERATED: {name} -->", f"<!-- END GENERATED: {name} -->"
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"README is missing the {name!r} generated block markers")
    return pattern.sub(f"{begin}\n{body}\n{end}", text)


def build() -> dict[Path, str]:
    s = load_spec()
    out = {SKILL: render_skill(s)}
    readme = README.read_text()
    for name, body in render_readme_blocks(s).items():
        readme = splice(readme, name, body)
    out[README] = readme
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 on drift instead of writing")
    args = ap.parse_args()

    drifted = []
    for path, content in build().items():
        current = path.read_text() if path.exists() else None
        if current == content:
            continue
        if args.check:
            drifted.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"wrote {path.relative_to(ROOT)}")

    if drifted:
        print("DRIFT — these generated files do not match data/:", file=sys.stderr)
        for p in drifted:
            print(f"  {p}", file=sys.stderr)
        print("\nRun `python3 scripts/build.py` and commit the result.", file=sys.stderr)
        return 1
    print("build: no drift" if args.check else "build: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
