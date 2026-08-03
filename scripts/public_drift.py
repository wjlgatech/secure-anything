#!/usr/bin/env python3
"""Has the published tree drifted from what this repo would export?

The public repo is GENERATED, so it can silently fall behind the private source of truth —
someone edits `data/registry.yml` here, forgets `make public`, and the public README quietly
describes a registry that no longer exists. A generated artifact with no drift check is just
a copy someone promised to keep updated.

Exports to a temp dir and diffs against the real public checkout. Read-only: it never writes
to the public tree and never pushes.

  exit 0 = in sync (or the public checkout is absent, reported as NOT MEASURED)
  exit 1 = drifted; run `make public` and push
"""
from __future__ import annotations

import filecmp
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from publish_public import DEFAULT_OUT, export  # noqa: E402

# Generated inside the public tree by its own `build.py`; not produced by the export itself.
GENERATED_IN_PUBLIC = {"README.md", "skills/secure-anything/SKILL.md"}


def main() -> int:
    live = DEFAULT_OUT
    if not live.is_dir():
        # No evidence means no — but this is genuinely unmeasurable, not a failure, so it is
        # reported by name rather than silently passing as "in sync".
        print(f"public_drift: NOT MEASURED — no public checkout at {live}")
        print("  (clone wjlgatech/secure-anything-core there to enable this check)")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        ref = Path(tmp) / "export"
        if export(ref, force=True) != 0:
            return 1

        def rel_files(base: Path) -> set[str]:
            return {
                p.relative_to(base).as_posix()
                for p in base.rglob("*")
                if p.is_file() and ".git" not in p.parts
                and not any(x in p.parts for x in ("__pycache__", ".pytest_cache",
                                                   ".ruff_cache", ".venv", "runs"))
            }

        want, have = rel_files(ref), rel_files(live)
        missing = sorted(want - have)
        extra = sorted(have - want)
        changed = sorted(
            f for f in (want & have) - GENERATED_IN_PUBLIC
            if not filecmp.cmp(ref / f, live / f, shallow=False)
        )

    if not (missing or extra or changed):
        print(f"public_drift: in sync — {len(want)} file(s) match the published tree")
        return 0

    print("PUBLIC TREE HAS DRIFTED from what this repo would export:", file=sys.stderr)
    for f in missing:
        print(f"  + {f}  (would be added)", file=sys.stderr)
    for f in extra:
        print(f"  - {f}  (published but no longer exported)", file=sys.stderr)
    for f in changed:
        print(f"  ~ {f}  (content differs)", file=sys.stderr)
    print("\nRun `make public`, then commit and push the public tree.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
