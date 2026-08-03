#!/usr/bin/env python3
"""The IP boundary, as an executable gate.

"We'll be careful about what goes public" is a promise. This is a check. It answers one
question: **would exporting the public subset leak anything?** Two independent walls, because
either alone fails eventually:

  WALL 1 — path allowlist. A file is publishable only if it matches PUBLIC_PATHS. Default is
           SECRET, not public: a new file added tomorrow is excluded until someone opts it in.
           (A denylist would silently publish whatever nobody thought to deny.)
  WALL 2 — content denylist. Even an allowlisted file is refused if it contains a term from
           SENSITIVE_TERMS. This catches the real failure mode: strategy leaking into a
           docstring, a client name in a comment, a pricing note in a test fixture.

Exit 0 = the public subset is safe to export. Anything else = do not publish.
"""
from __future__ import annotations

import re
import sys
from fnmatch import fnmatch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── WALL 1: only these may ever go public (default-deny) ────────────────────────────────
PUBLIC_PATHS = [
    # the lean composition core — but NOT organs/
    "src/secure_anything/__init__.py",
    "src/secure_anything/spec.py",
    "src/secure_anything/router.py",
    "src/secure_anything/gate.py",
    "src/secure_anything/coverage.py",
    "src/secure_anything/ledger.py",
    "src/secure_anything/store.py",
    "src/secure_anything/signing.py",
    # the ecosystem — the actual gift to the community
    "data/*.yml",
    "scripts/*.py",
    "eval/*.md",
    "skills/secure-anything/*.md",
    "docs/satellites/*.md",
    # tests that exercise only the core
    "tests/test_core_invariants.py",
    "tests/test_gate_seam.py",
    "tests/test_spec_and_coverage.py",
    "tests/test_router_eval.py",
    "tests/test_ledger_chain.py",
    "tests/test_ledger_signing.py",
    "tests/conftest_public.py",
    # public-facing docs (generated or hand-written FOR the public tree)
    "README.md", "LICENSE", "LICENSE-DATA", "CONTRIBUTING.md", "CHANGELOG.md",
    "AGENTS.md", "llms.txt", "Makefile", "pyproject.toml", ".gitignore",
    "docs/VISION.md", "ROADMAP.md",
    ".github/workflows/ci.yml", ".github/ISSUE_TEMPLATE/*.md",
]

# Never publishable, even if a glob above would otherwise match.
ALWAYS_PRIVATE = [
    "src/secure_anything/organs/*", "docs/organs/*", "docs/adr/*", "docs/specs/*",
    "docs/0*.md", "GOAL.md", "scripts/publish_gate.py", "scripts/publish_public.py",
    "scripts/demo_bypass_caught.py", "docs/*PLAYBOOK*.md", "CLAUDE.md",
    ".env*", "Dockerfile", "docker-compose.yml",
]

# ── WALL 2: strategy/commercial terms that must never appear in a published file ────────
SENSITIVE_TERMS = [
    r"design partner", r"buyer hypothes", r"who holds the budget", r"go-to-market",
    r"\bGTM\b", r"pricing", r"\bARR\b", r"revenue", r"Accenture", r"pilot program",
    r"competitive landscape", r"demand signal", r"switching cost", r"our moat",
    r"secure-anything-private", r"Braintrust ~\$", r"90-day pilot",
]
# Phrases that legitimately contain a sensitive-looking word in a non-strategy sense.
# An exception only excuses a hit whose span falls INSIDE the exception's own span.
# It must never excuse "everything nearby" — an earlier version matched on a +/-60 char
# context window, so the word "moat" anywhere on a line silently excused a planted
# "pricing ... design partner" leak on that same line. The gate reported SAFE. Caught
# 2026-08-03 by deliberately planting a violation, which is now a test.
ALLOWED_EXCEPTIONS = [
    r"pricing page",   # evidence-ladder example: "read the PRICING PAGE for a price"
]


def is_public(rel: str) -> bool:
    if any(fnmatch(rel, pat) for pat in ALWAYS_PRIVATE):
        return False
    return any(fnmatch(rel, pat) for pat in PUBLIC_PATHS)


def scan_content(rel: str, text: str) -> list[str]:
    # Spans that an exception legitimately covers. A hit is excused ONLY if it sits
    # entirely inside one of these — never merely near one.
    excused = [m.span() for exc in ALLOWED_EXCEPTIONS
               for m in re.finditer(exc, text, re.I)]
    hits = []
    for term in SENSITIVE_TERMS:
        for m in re.finditer(term, text, re.I):
            if any(lo <= m.start() and m.end() <= hi for lo, hi in excused):
                continue
            ctx = text[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")
            line = text[:m.start()].count("\n") + 1
            hits.append(f"{rel}:{line}: matches /{term}/ — …{ctx.strip()}…")
    return hits


def public_files() -> list[Path]:
    out = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or ".git/" in p.as_posix():
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(part in (".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache")
               for part in p.parts):
            continue
        if is_public(rel):
            out.append(p)
    return out


def main() -> int:
    files = public_files()
    leaks: list[str] = []
    for p in files:
        try:
            leaks += scan_content(p.relative_to(ROOT).as_posix(), p.read_text())
        except UnicodeDecodeError:
            leaks.append(f"{p}: binary file in the public set — refuse")

    print(f"publish_gate: {len(files)} file(s) pass the path allowlist")
    if leaks:
        print("\nBOUNDARY VIOLATION — these publishable files contain private terms:",
              file=sys.stderr)
        for line in leaks:
            print(f"  ✗ {line}", file=sys.stderr)
        print(f"\n{len(leaks)} violation(s). DO NOT PUBLISH.", file=sys.stderr)
        return 1
    print("publish_gate: no sensitive terms in the public subset — safe to export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
