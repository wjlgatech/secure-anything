"""The router: a messy intent in, a deterministic hand-off out.

No LLM, no scoring heuristics that drift — substring matching over triggers declared in
data/*.yml. Every routing claim in eval/secure-anything.md is a pytest case, including the
refusals: a license wall must refuse, and a no-match must BANK THE GAP rather than guess.
"""
from __future__ import annotations

import re

from pydantic import BaseModel, Field

from .spec import Capability, KnowledgeCard, Spec, spec


class Route(BaseModel):
    intent: str
    capabilities: list[Capability] = Field(default_factory=list)
    cards: list[KnowledgeCard] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def matched(self) -> bool:
        return bool(self.capabilities or self.cards)

    @property
    def gap(self) -> str:
        """A no-match is a finding, not a failure — it names what the ecosystem lacks."""
        return "" if self.matched else f"No capability or knowledge card covers: {self.intent!r}"

    @property
    def top(self) -> Capability | None:
        return self.capabilities[0] if self.capabilities else None


def _hits(intent: str, triggers: list[str]) -> int:
    """Longest matching trigger wins — a specific phrase beats an incidental word.

    Matching is word-bounded, not naive substring: otherwise the trigger `opa` fires on
    "opaque" and `gap` fires on "gaps". (Earned 2026-08-03 from the eval suite.)
    """
    return max(
        (len(t) for t in triggers if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", intent)),
        default=0,
    )


def route(intent: str, s: Spec | None = None) -> Route:
    s = s or spec()
    low = " ".join(intent.lower().split())

    caps = sorted(
        ((c, _hits(low, c.triggers)) for c in s.capabilities),
        key=lambda p: (-p[1], -p[0].status.rank, p[0].id),
    )
    cards = sorted(
        ((c, _hits(low, c.triggers)) for c in s.cards),
        key=lambda p: (-p[1], p[0].id),
    )
    r = Route(
        intent=intent,
        capabilities=[c for c, h in caps if h > 0],
        cards=[c for c, h in cards if h > 0],
    )

    for c in r.capabilities:
        if c.pointer_only and c.kind == "external":
            r.warnings.append(
                f"{c.id}: license {c.license or 'UNKNOWN'} is unconfirmed — POINTER ONLY. "
                "Run it upstream; do not vendor it and do not execute it in our CI."
            )
    for c in r.cards:
        if c.unconfirmed:
            r.warnings.append(f"{c.id}: {c.evidence.value} — {c.unconfirmed.strip()}")
    return r
