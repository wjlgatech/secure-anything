"""The north star: Verified Control Coverage (VCC).

VCC = |controls with >=1 integrated capability holding a run receipt| / |controls in scope|

Ungameable by hoarding: a ⚪ candidate or a 🟡 digest contributes ZERO. Only a capability
that ran here and left a receipt moves the number. See docs/VISION.md.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from .spec import Spec, Status, spec

RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"


class Coverage(BaseModel):
    covered: list[str] = Field(default_factory=list)
    uncovered: list[str] = Field(default_factory=list)
    proven_by: dict[str, list[str]] = Field(default_factory=dict)
    claimed_only: list[str] = Field(default_factory=list)  # mapped, but no receipt yet

    @property
    def total(self) -> int:
        return len(self.covered) + len(self.uncovered)

    @property
    def vcc(self) -> float:
        return len(self.covered) / self.total if self.total else 0.0


def receipts_on_disk(runs_dir: Path | None = None) -> set[str]:
    d = runs_dir or RUNS_DIR
    if not d.is_dir():
        return set()
    return {p.name for p in d.iterdir() if p.is_dir() and any(p.iterdir())}


def compute(s: Spec | None = None, receipts: set[str] | None = None) -> Coverage:
    s = s or spec()
    have = receipts if receipts is not None else receipts_on_disk()

    proving: dict[str, list[str]] = {}
    mapped: dict[str, list[str]] = {}
    for cap in s.capabilities:
        for ctrl in cap.covers:
            mapped.setdefault(ctrl, []).append(cap.id)
            if cap.status is Status.INTEGRATED and cap.id in have:
                proving.setdefault(ctrl, []).append(cap.id)

    all_ids = [c.id for c in s.controls]
    covered = [c for c in all_ids if c in proving]
    return Coverage(
        covered=covered,
        uncovered=[c for c in all_ids if c not in proving],
        proven_by=proving,
        claimed_only=[c for c in all_ids if c in mapped and c not in proving],
    )
