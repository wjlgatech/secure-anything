from agentgate.decision import decide
from agentgate.domain import ActionType, ActorKind, CheckResult, RiskTier


def _clean() -> list[CheckResult]:
    return [CheckResult(name="x", passed=True)]


def test_human_low_risk_auto_approves(make_pr, policy):
    d = decide(make_pr(ActorKind.HUMAN), _clean(), policy)
    assert d.action is ActionType.AUTO_APPROVE and d.risk is RiskTier.LOW


def test_human_medium_auto_approves_agent_does_not(make_pr, policy):
    medium = [CheckResult(name="diff_size", passed=False, severity=RiskTier.MEDIUM, detail="big")]
    # human policy allows auto-approve up to medium
    dh = decide(make_pr(ActorKind.HUMAN), medium, policy)
    assert dh.action is ActionType.AUTO_APPROVE
    # ai agent must escalate on medium
    da = decide(make_pr(ActorKind.AI_AGENT), medium, policy)
    assert da.action is ActionType.ESCALATE


def test_high_risk_escalates_for_everyone(make_pr, policy):
    high = [CheckResult(name="touched_paths", passed=False, severity=RiskTier.HIGH, detail="infra")]
    for kind in (ActorKind.HUMAN, ActorKind.AI_AGENT, ActorKind.BOT):
        assert decide(make_pr(kind), high, policy).action is ActionType.ESCALATE


def test_secret_blocks_with_request_changes(make_pr, policy):
    blocking = [CheckResult(name="secret_scan", passed=False, severity=RiskTier.HIGH,
                            blocking=True, detail="secret")]
    d = decide(make_pr(ActorKind.HUMAN), blocking, policy)
    assert d.action is ActionType.REQUEST_CHANGES


def test_no_evidence_escalates_when_llm_expected(make_pr, policy):
    medium = [CheckResult(name="diff_size", passed=False, severity=RiskTier.MEDIUM, detail="big")]
    # human would normally auto-approve medium, but if an LLM review was expected
    # and came back unavailable, we escalate rather than approve on missing evidence.
    d = decide(make_pr(ActorKind.HUMAN), medium, policy, llm=None, llm_expected=True)
    assert d.action is ActionType.ESCALATE
    assert any("no evidence" in r for r in d.reasons)
