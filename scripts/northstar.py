#!/usr/bin/env python3
"""Compute and print the north star: Verified Control Coverage.

Offline, from data/ plus the receipts on disk. Presentation lives here, not in the core.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from secure_anything.coverage import compute, receipts_on_disk  # noqa: E402
from secure_anything.spec import load_spec  # noqa: E402


def render() -> str:
    s = load_spec()
    cov = compute(s, receipts=receipts_on_disk())
    lines = [
        f"Verified Control Coverage (VCC): {len(cov.covered)}/{cov.total} = {cov.vcc:.1%}"
    ]
    if not cov.covered:
        lines.append("  (zero is the honest answer at this milestone — the number IS the queue)")
    for c in cov.covered:
        lines.append(f"  ✅ {c}: proven by {', '.join(cov.proven_by[c])}")
    if cov.claimed_only:
        lines.append(
            f"  ⚠️  {len(cov.claimed_only)} control(s) MAPPED to a capability but with no run "
            f"receipt — mapped is not measured: {', '.join(cov.claimed_only)}"
        )
    uncovered_unmapped = [c for c in cov.uncovered if c not in cov.claimed_only]
    if uncovered_unmapped:
        lines.append(
            f"  ⬜ {len(uncovered_unmapped)} control(s) with NO capability at all — the honest "
            f"gap: {', '.join(uncovered_unmapped)}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(render())
