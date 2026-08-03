#!/usr/bin/env python3
"""Refuse any status promotion whose on-disk evidence is missing.

The maker is not the checker: `scripts/build.py` renders the registry, this script
independently disbelieves it. A ladder that promotes on assertion is a hoard with emoji.

Exit 0 = every claim in data/ is backed by something on disk.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from secure_anything.spec import Evidence, Status, load_spec  # noqa: E402

NUMERIC = tuple("0123456789")


def check() -> list[str]:
    s = load_spec()
    bad: list[str] = []

    for c in s.capabilities:
        where = f"registry/{c.id}"

        if c.status.rank >= Status.DIGESTED.rank:
            digest = ROOT / "docs" / "satellites" / f"{c.id}.md"
            if not digest.exists():
                bad.append(
                    f"{where}: status={c.status.value} but "
                    f"{digest.relative_to(ROOT)} is missing"
                )
            if c.kind == "external" and not c.pinned_sha:
                bad.append(f"{where}: external capability at {c.status.value} without a pinned_sha")

        if c.status is Status.INTEGRATED:
            runs = ROOT / "runs" / c.id
            if not runs.is_dir() or not any(runs.iterdir()):
                bad.append(f"{where}: integrated but no run receipt under runs/{c.id}/")
            if c.pointer_only:
                bad.append(f"{where}: integrated on an unconfirmed licence ({c.license or 'none'})")

        if c.license in ("", "NOASSERTION") and c.license_confirmed:
            bad.append(f"{where}: license_confirmed=true but no SPDX licence recorded")
        if c.covers and not c.verified_at:
            bad.append(f"{where}: maps to controls but has no verified_at date")

    known = {ctrl.id for ctrl in s.controls}
    for c in list(s.capabilities) + list(s.cards):
        unknown = set(c.covers) - known
        if unknown:
            bad.append(f"{c.id}: maps to controls absent from data/controls.yml: {sorted(unknown)}")

    for card in s.cards:
        where = f"knowledge/{card.id}"
        if not card.verified_at:
            bad.append(f"{where}: no verified_at date")
        if card.unconfirmed and card.evidence is Evidence.VERIFIED:
            bad.append(f"{where}: claims `verified` while carrying an `unconfirmed` note")
        if card.evidence is Evidence.VERIFIED and not card.url:
            bad.append(f"{where}: `verified` requires a resolvable url to the primary source")
        # A number in a summary must be traceable: below `corroborated`, say so explicitly.
        text = f"{card.summary} {card.why_it_matters}"
        if any(ch in text for ch in NUMERIC) and card.evidence is Evidence.CLAIMED:
            if not card.unconfirmed:
                bad.append(f"{where}: `claimed` card states figures without an `unconfirmed` note")

    return bad


def main() -> int:
    problems = check()
    if problems:
        print("REGISTRY/KNOWLEDGE EVIDENCE FAILURES:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        print(f"\n{len(problems)} claim(s) not backed by on-disk evidence.", file=sys.stderr)
        return 1
    s = load_spec()
    print(f"verify_registry: ok — {len(s.capabilities)} capabilities, {len(s.cards)} cards, "
          f"{len(s.controls)} controls, every claim backed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
