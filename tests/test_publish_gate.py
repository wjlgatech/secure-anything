"""The IP boundary must actually fire. PRIVATE-ONLY test (never exported).

Origin: on 2026-08-03 the gate reported SAFE on a file containing
"our moat is the ledger; pricing starts at $500/mo per design partner" — three separate
denied terms — because `ALLOWED_EXCEPTIONS` was matched against a ±60-character context
window, so the incidental word "moat" excused every other hit nearby. A validator that has
never fired on you is probably not checking anything, so it now gets fired at on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from publish_gate import ALWAYS_PRIVATE, is_public, scan_content

MUST_STAY_PRIVATE = [
    "docs/01-MARKET.md",
    "docs/00-BACKGROUND.md",
    "docs/06-DESIGN-PARTNERS.md",
    "docs/08-BENCHMARKING.md",
    "docs/09-TRUST-AS-A-SERVICE.md",
    "docs/03-ARCHITECTURE.md",
    "docs/04-SECURITY.md",
    "docs/05-POLICY.md",
    "docs/07-PRIOR-ART.md",
    "GOAL.md",
    "CLAUDE.md",
    "docs/META_REPO_PLAYBOOK.md",
    "docs/REPO_PLAYBOOK.md",
    "docs/adr/005-meta-repo-restructure.md",
    "docs/specs/phase-4-scale-gtm.md",
    "docs/organs/agentgate/README.md",
    "src/secure_anything/organs/agentgate/worker.py",
    "src/secure_anything/organs/agentgate/policy/default_policy.yaml",
    "scripts/publish_gate.py",
    ".env.example",
]

MUST_BE_PUBLIC = [
    "src/secure_anything/router.py",
    "src/secure_anything/gate.py",
    "data/registry.yml",
    "data/knowledge.yml",
    "eval/secure-anything.md",
    "tests/test_gate_seam.py",
]

LEAKS = [
    "our moat is the ledger",
    "pricing starts at $500/mo",
    "recruit 3-5 design partners",
    "the buyer hypotheses table",
    "this is an Accenture engagement",
    "see wjlgatech/secure-anything-private for the organ",
    "our go-to-market motion",
    "the 90-day pilot outcome",
]


@pytest.mark.parametrize("rel", MUST_STAY_PRIVATE)
def test_private_path_is_never_publishable(rel: str):
    assert not is_public(rel), f"{rel} would be PUBLISHED — the IP boundary is broken"


@pytest.mark.parametrize("rel", MUST_BE_PUBLIC)
def test_public_path_is_publishable(rel: str):
    assert is_public(rel), f"{rel} is blocked; the public tree would be incomplete"


def test_default_is_deny_not_allow():
    """A file nobody thought about must be private, not public."""
    assert not is_public("docs/some-new-strategy-doc-written-tomorrow.md")
    assert not is_public("src/secure_anything/organs/newthing/secret.py")


@pytest.mark.parametrize("leak", LEAKS)
def test_content_wall_catches_a_planted_leak(leak: str):
    assert scan_content("data/knowledge.yml", f"# {leak}\n"), f"NOT caught: {leak!r}"


def test_an_exception_excuses_only_itself_not_the_whole_line():
    """The exact bug: an allowed phrase must not excuse other hits sharing its line."""
    line = "read the pricing page for a price; our moat is the ledger; design partner deck\n"
    hits = scan_content("x.md", line)
    assert hits, "the exception swallowed real violations again"
    assert any("our moat" in h for h in hits)
    assert any("design partner" in h for h in hits)


def test_the_allowed_exception_still_works():
    """…while a genuine false positive stays excused."""
    assert not scan_content("x.md", "the evidence ladder says: read the PRICING PAGE for a price")


def test_organs_are_categorically_private():
    assert "src/secure_anything/organs/*" in ALWAYS_PRIVATE
