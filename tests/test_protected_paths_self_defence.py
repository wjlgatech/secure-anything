"""The gate must protect the code and the spec that decide its own behaviour.

Regression test for a silent un-protection found on 2026-08-03: the default policy listed the
literal glob `src/agentgate/policy/**`, which stopped matching anything the moment the organ
moved to `src/secure_anything/organs/agentgate/policy/`. Nothing failed — the gate simply
stopped guarding its own policy. A path written as a fixed prefix is a time bomb; these
assertions are written against the paths that ACTUALLY exist today.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from secure_anything.organs.agentgate.checks.paths import path_matches
from secure_anything.organs.agentgate.policy import DEFAULT_POLICY_PATH
from secure_anything.organs.agentgate.policy.engine import load_policy

ROOT = Path(__file__).resolve().parents[1]

# Real, on-disk paths whose modification must never be auto-approved.
MUST_BE_PROTECTED = [
    "src/secure_anything/organs/agentgate/policy/default_policy.yaml",
    "src/secure_anything/organs/agentgate/policy/schema.py",
    "src/secure_anything/ledger.py",
    "src/secure_anything/signing.py",
    "data/registry.yml",
    "data/controls.yml",
    "data/ainative.yml",
    ".github/workflows/ci.yml",
]


@pytest.mark.parametrize("rel", MUST_BE_PROTECTED)
def test_self_governing_file_is_protected(rel: str):
    assert (ROOT / rel).exists(), f"{rel} does not exist — fix the test, not the policy"
    protected = load_policy(DEFAULT_POLICY_PATH).checks.touched_paths.protected
    assert any(path_matches(rel, g) for g in protected), (
        f"{rel} is NOT covered by any protected glob: {protected}"
    )


def test_an_ordinary_source_file_is_not_protected():
    """The guard must be specific — protecting everything protects nothing."""
    protected = load_policy(DEFAULT_POLICY_PATH).checks.touched_paths.protected
    assert not any(path_matches("README.md", g) for g in protected)


def test_no_protected_glob_hardcodes_the_package_prefix():
    """A glob anchored to `src/<pkg>/` breaks silently on the next move."""
    for glob in load_policy(DEFAULT_POLICY_PATH).checks.touched_paths.protected:
        assert not glob.startswith("src/secure_anything/"), (
            f"{glob!r} hardcodes the package path — use a name-based glob like '**/policy/**'"
        )
