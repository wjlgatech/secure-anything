"""Every routing claim in eval/secure-anything.md is a test — including the refusals.

The eval file is the spec; this module is the only thing that makes it true. If a row is
added there and the router can't satisfy it, the build fails.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from secure_anything.router import route

EVAL = Path(__file__).resolve().parents[1] / "eval" / "secure-anything.md"
SYNTAX_ROWS = {"capability:<id>", "capability?<id>", "card:<id>", "warn:<id>", "gap"}


def cases() -> list[tuple[str, str]]:
    rows = []
    for line in EVAL.read_text().splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|", line)
        if m and m.group(1) not in SYNTAX_ROWS:  # skip the syntax-legend table
            rows.append((m.group(1), m.group(2)))
    return rows


def test_eval_file_has_cases():
    assert len(cases()) >= 20, "the eval file should be the router's real spec, not a sample"


@pytest.mark.parametrize("intent,expect", cases(), ids=lambda v: v[:48])
def test_routing_case(intent: str, expect: str):
    r = route(intent)
    kind, _, target = expect.partition(":") if ":" in expect else expect.partition("?")
    ids = [c.id for c in r.capabilities]
    card_ids = [c.id for c in r.cards]

    if expect == "gap":
        assert not r.matched, f"expected a banked gap, got {ids or card_ids}"
        assert r.gap.startswith("No capability or knowledge card covers")
    elif "?" in expect:
        _, _, target = expect.partition("?")
        assert target in ids, f"{target!r} not in matched capabilities {ids}"
    elif kind == "capability":
        assert ids and ids[0] == target, f"top match was {ids[:3]}, expected {target!r}"
    elif kind == "card":
        assert target in card_ids, f"{target!r} not in matched cards {card_ids}"
    elif kind == "warn":
        assert any(w.startswith(f"{target}:") for w in r.warnings), (
            f"expected a warning for {target!r}, got {r.warnings}"
        )
    else:
        pytest.fail(f"unknown expectation syntax: {expect!r}")


def test_a_license_wall_always_warns_for_external_pointer_only():
    """Structural, not just case-by-case: no unconfirmed-license external repo is ever
    routed without saying so."""
    from secure_anything.spec import spec

    for cap in spec().capabilities:
        if cap.kind == "external" and cap.pointer_only and cap.triggers:
            r = route(cap.triggers[0])
            assert any(cap.id in w for w in r.warnings), f"{cap.id} routed with no license warning"


def test_router_is_deterministic():
    assert [c.id for c in route("scan my repo").capabilities] == \
           [c.id for c in route("Scan  My   Repo").capabilities]
