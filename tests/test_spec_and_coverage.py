"""The spec loads, and the north star cannot be gamed by hoarding."""
from secure_anything.coverage import compute
from secure_anything.spec import Evidence, Status, load_spec, spec


def test_spec_loads_all_four_data_files():
    s = spec()
    assert s.capabilities and s.cards and s.frameworks and s.principles


def test_control_denominator_is_the_two_owasp_lists():
    s = spec()
    ids = [c.id for c in s.controls]
    assert len([i for i in ids if i.startswith("LLM")]) == 10
    assert len([i for i in ids if i.startswith("ASI")]) == 10
    assert len(ids) == len(set(ids)), "duplicate control ids"


def test_every_capability_covers_only_real_controls():
    s = spec()
    known = {c.id for c in s.controls}
    for cap in s.capabilities:
        unknown = set(cap.covers) - known
        assert not unknown, f"{cap.id} maps to controls not in data/controls.yml: {unknown}"


def test_every_knowledge_card_covers_only_real_controls():
    s = spec()
    known = {c.id for c in s.controls}
    for card in s.cards:
        unknown = set(card.covers) - known
        assert not unknown, f"{card.id} maps to unknown controls: {unknown}"


def test_ids_are_unique():
    s = spec()
    for label, items in (("capability", s.capabilities), ("card", s.cards)):
        ids = [i.id for i in items]
        assert len(ids) == len(set(ids)), f"duplicate {label} id"


def test_unconfirmed_claims_are_never_tiered_verified():
    for card in spec().cards:
        if card.unconfirmed:
            assert card.evidence is not Evidence.VERIFIED, (
                f"{card.id} carries an `unconfirmed` note but claims `verified`"
            )


def test_unresolved_license_means_pointer_only():
    for cap in spec().capabilities:
        if cap.license in ("", "NOASSERTION"):
            assert cap.pointer_only, f"{cap.id} has no confirmed license but is not pointer-only"
            assert cap.status is not Status.INTEGRATED, (
                f"{cap.id} cannot be integrated on an unconfirmed license"
            )


def test_naming_a_satellite_does_not_move_the_north_star():
    """The whole point of the ladder: hoarding is worth zero."""
    s = load_spec()
    for cap in s.capabilities:
        cap.status = Status.DIGESTED  # pretend everything is digested
    assert compute(s, receipts=set()).vcc == 0.0


def test_only_an_integrated_capability_with_a_receipt_counts():
    s = load_spec()
    cap = next(c for c in s.capabilities if c.covers)
    cap.status = Status.INTEGRATED
    assert compute(s, receipts=set()).vcc == 0.0, "integrated without a receipt must count zero"
    cov = compute(s, receipts={cap.id})
    assert cov.vcc > 0.0
    assert set(cov.proven_by[cap.covers[0]]) == {cap.id}


def test_mapped_but_unproven_controls_are_reported_not_counted():
    """Mapped is not measured: a control someone claimed is separate from one that is proven."""
    cov = compute(load_spec(), receipts=set())
    assert cov.claimed_only, "controls are mapped in the registry"
    assert not cov.covered
    assert set(cov.claimed_only).isdisjoint(cov.covered)
