"""Architectural invariants as executable tests.

GOAL.md G2 (lean core) and G3 (no domain logic in the core) are budgets with teeth, not
aspirations. A meta-repo that quietly grows domain logic has failed at its one job, and the
only thing that reliably prevents it is a test that fails.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src" / "secure_anything"
CORE_LOC_BUDGET = 600

# Names that betray domain logic leaking into the composition layer. If the core ever needs
# to know about a specific vendor or wire protocol, that knowledge belongs in an organ.
DOMAIN_SMELLS = (
    "github", "gitlab", "semgrep", "codeql", "webhook", "openai", "anthropic",
    "slack", "jira", "docker", "kubernetes",
)


def core_files() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.py") if "organs" not in p.parts)


def test_core_files_exist():
    assert {p.stem for p in core_files()} >= {
        "spec", "router", "gate", "ledger", "coverage", "signing", "store"
    }


def test_core_is_lean():
    """G2: the composition core fits in a budget."""
    sizes = {p.relative_to(SRC).as_posix(): len(p.read_text().splitlines()) for p in core_files()}
    total = sum(sizes.values())
    assert total <= CORE_LOC_BUDGET, (
        f"core is {total} LOC, budget {CORE_LOC_BUDGET}. Push logic into an organ, "
        f"not into the core.\n" + "\n".join(f"  {k}: {v}" for k, v in sorted(sizes.items()))
    )


@pytest.mark.parametrize("path", core_files(), ids=lambda p: p.name)
def test_core_never_imports_an_organ(path: Path):
    """G2/G3: dependency direction is organ -> core, never the reverse."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        mod = ""
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
        elif isinstance(node, ast.Import):
            mod = ",".join(a.name for a in node.names)
        assert "organs" not in mod, f"{path.name} imports an organ: {mod}"


@pytest.mark.parametrize("path", core_files(), ids=lambda p: p.name)
def test_core_names_no_vendor_or_protocol(path: Path):
    """G3: the core must not know what a GitHub is."""
    text = path.read_text().lower()
    # Comments and docstrings may discuss the world; code may not depend on it.
    code = "\n".join(
        line.split("#")[0] for line in text.splitlines() if not line.strip().startswith("#")
    )
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
            doc = ast.get_docstring(node)
            if doc:
                code = code.replace(doc.lower(), "")
    hits = [s for s in DOMAIN_SMELLS if s in code]
    assert not hits, f"{path.name} references domain/vendor names in code: {hits}"


def test_no_vendored_satellite_trees():
    """Meta law: satellites are pointers, never forks."""
    root = SRC.parents[1]
    for bad in ("vendor", "third_party", "vendored"):
        assert not (root / bad).exists(), f"{bad}/ exists — satellites must never be vendored"
    nested_git = [p for p in (root / "src").rglob(".git") if p.is_dir()]
    assert not nested_git, f"nested git checkouts found (vendored satellite?): {nested_git}"
