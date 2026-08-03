#!/usr/bin/env python3
"""Export the public subset of this repo into a separate, fresh-history public tree.

WHY a separate tree and not `gh repo edit --visibility public`:
flipping this repo would publish ALL of git history — every commit still contains the market
research, the partner program and the positioning docs. Squashing does not help; history is
recoverable. A fresh tree with a fresh history is the only honest way to publish work that was
developed in private.

The private repo stays the single source of truth. The public tree is GENERATED — the same
discipline the rest of this repo already uses for the README and the flagship skill.

Nothing is exported unless `scripts/publish_gate.py` exits 0.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publish_gate import main as gate_main  # noqa: E402
from publish_gate import public_files  # noqa: E402

DEFAULT_OUT = ROOT.parent / "secure-anything-public"
OVERRIDES = ROOT / "publish" / "overrides"
PRIVATE_ORGAN_URL = "https://github.com/wjlgatech/secure-anything-lab"


def transform_registry(text: str) -> str:
    """The agentgate organ does not exist in the public tree. It becomes what it honestly
    is from the outside: a private capability, pointer-only, at ⚪ candidate."""
    old_block_start = "  - id: agentgate\n"
    i = text.index(old_block_start)
    j = text.index("\n  - id: ", i + 1) + 1
    new = f"""  - id: agentgate
    kind: family
    role: gate
    capability: "Actor-aware PR firewall for human + AI-agent code changes: verify -> classify actor -> deterministic checks -> actor-aware decision -> hash-chained, signed audit"
    url: {PRIVATE_ORGAN_URL}
    status: candidate
    license: "Proprietary"
    license_confirmed: true
    visibility: private
    verified_at: "2026-08-03"
    covers: []
    notes: >-
      The reference organ built on this core, developed privately. Listed as a pointer so the
      routing surface is honest about what exists; it is NOT distributed here and contributes
      ZERO to the north star (no public run receipt). The composition core it runs on IS here,
      in full — an organ is ~200 lines of adapter over it.
    triggers: ["review this pr", "gate a pull request", "block an agent pr", "pr firewall", "actor-aware"]

"""
    return text[:i] + new + text[j:]


def transform_manifest(text: str) -> str:
    """The public tree ships a different (smaller) document set."""
    for block in ("  GOAL.md:", "  docs/organs/agentgate/README.md:"):
        i = text.find(block)
        if i == -1:
            continue
        nxt = text.find("\n  ", text.index("\n", i) + 1)
        while nxt != -1 and text[nxt:nxt + 4] == "\n   ":
            nxt = text.find("\n  ", nxt + 1)
        text = text[:i] + text[nxt + 1:] if nxt != -1 else text[:i]
    return text


TRANSFORMS = {"data/registry.yml": transform_registry, "data/manifest.yml": transform_manifest}


def export(out: Path, *, force: bool) -> int:
    if gate_main() != 0:
        print("\nexport ABORTED — the publish gate refused.", file=sys.stderr)
        return 1

    if out.exists():
        if not force:
            print(f"{out} exists; pass --force to overwrite its working tree", file=sys.stderr)
            return 1
        for child in out.iterdir():
            if child.name != ".git":
                shutil.rmtree(child) if child.is_dir() else child.unlink()
    out.mkdir(parents=True, exist_ok=True)

    n = 0
    for src in public_files():
        rel = src.relative_to(ROOT).as_posix()
        dst = out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text()
        if rel in TRANSFORMS:
            text = TRANSFORMS[rel](text)
        dst.write_text(text)
        n += 1

    # The exporter itself is private; strip it from the public scripts/ dir.
    for gone in ("publish_gate.py", "publish_public.py"):
        (out / "scripts" / gone).unlink(missing_ok=True)
    # The organ has no digest in the public tree (it ships as a candidate pointer).
    (out / "docs" / "satellites" / "agentgate.md").unlink(missing_ok=True)

    # Deliberate public wording beats wording derived by accident.
    for src in sorted(OVERRIDES.rglob("*")):
        if src.is_file():
            rel = src.relative_to(OVERRIDES)
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"  override: {rel}")
            n += 1

    # Regenerate the public tree's own surfaces: its registry differs (the organ is a
    # pointer there), so its README tables and SKILL.md must be built FROM its own data.
    r = subprocess.run([sys.executable, "scripts/build.py"], cwd=out, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout + r.stderr, file=sys.stderr)
        return r.returncode

    print(f"\nexported {n} file(s) -> {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--verify", action="store_true", help="run `make check` in the exported tree")
    a = ap.parse_args()

    rc = export(a.out, force=a.force)
    if rc or not a.verify:
        return rc

    print("\n── verifying the exported tree stands alone ──")
    r = subprocess.run(["make", "check"], cwd=a.out)
    if r.returncode:
        print("\nthe exported tree does NOT pass its own gate — do not publish it",
              file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
