#!/usr/bin/env python3
"""Charter manifest gate — the docs are gated like code.

A greenfield doc phase has no compiler, so build the finish line first: a file must exist,
carry its required headings, and clear a minimum size. Prose that can drift silently is
prose nobody maintains.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _manifest() -> dict:
    import yaml
    return yaml.safe_load((ROOT / "data" / "manifest.yml").read_text())["documents"]


MANIFEST: dict[str, dict] = _manifest()


def check() -> list[str]:
    bad = []
    for rel, spec in MANIFEST.items():
        p = ROOT / rel
        if not p.exists():
            bad.append(f"{rel}: MISSING")
            continue
        text = p.read_text()
        words = len(text.split())
        if words < spec["min_words"]:
            bad.append(f"{rel}: {words} words < required {spec['min_words']}")
        for h in spec["headings"]:
            if h not in text:
                bad.append(f"{rel}: missing required heading {h!r}")
        for token in spec["must_contain"]:
            if token not in text:
                bad.append(f"{rel}: missing required content {token!r}")
    return bad


def main() -> int:
    problems = check()
    if problems:
        print("CHARTER MANIFEST GATE FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    print(f"manifest_gate: ok — {len(MANIFEST)} documents present and complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
