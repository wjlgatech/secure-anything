"""The gate seam's two invariants: exit codes not claims, and no-evidence-means-no."""
from secure_anything.gate import Aggregate, GateResult, Verdict


def test_exit_code_zero_is_pass_nonzero_is_fail():
    assert GateResult.from_exit_code("x", 0).verdict is Verdict.PASS
    assert GateResult.from_exit_code("x", 1).verdict is Verdict.FAIL
    assert GateResult.from_exit_code("x", 137).verdict is Verdict.FAIL


def test_not_measured_carries_no_exit_code():
    """We never invent a 0 for something that did not run."""
    r = GateResult.not_measured("codex-security", "no API credential in the offline gate")
    assert r.exit_code is None
    assert r.verdict is Verdict.NOT_MEASURED


def test_blocking_aggregate_cannot_pass_on_unmeasured():
    agg = Aggregate(results=[
        GateResult.from_exit_code("semgrep", 0),
        GateResult.not_measured("codex-security", "needs network"),
    ], blocking=True)
    assert not agg.passed
    assert agg.exit_code == 1
    assert [r.capability for r in agg.unmeasured] == ["codex-security"]


def test_non_blocking_aggregate_may_pass_while_reporting_unmeasured():
    agg = Aggregate(results=[
        GateResult.from_exit_code("semgrep", 0),
        GateResult.not_measured("codex-security", "needs network"),
    ], blocking=False)
    assert agg.passed
    assert agg.unmeasured, "an unmeasured item is still REPORTED, never hidden"


def test_empty_blocking_aggregate_is_not_a_pass():
    """Absence of evidence is not evidence of safety."""
    assert not Aggregate(results=[], blocking=True).passed


def test_a_single_failure_sinks_the_aggregate():
    agg = Aggregate(results=[
        GateResult.from_exit_code("a", 0), GateResult.from_exit_code("b", 2)
    ])
    assert not agg.passed and agg.exit_code == 1


def test_report_names_unmeasured_capabilities():
    agg = Aggregate(results=[GateResult.not_measured("garak", "not installed")])
    out = agg.report()
    assert "NOT MEASURED" in out and "garak" in out and "never counted as a pass" in out
