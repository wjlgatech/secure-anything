"""agent_audit check — deterministic, offline. The scanner is injected as a fake,
so no `agent-audit` binary or subprocess is ever touched here."""
from __future__ import annotations

from secure_anything.organs.agentgate.checks.agent_audit import (
    AgentAuditCheck,
    AgentAuditFinding,
    SubprocessAgentAuditScanner,
    parse_sarif,
)
from secure_anything.organs.agentgate.domain import RiskTier


class _FakeScanner:
    def __init__(self, result):
        self._result = result
        self.calls = 0

    def scan(self, files):
        self.calls += 1
        return self._result


def _enable(policy, min_level="warning"):
    policy.checks.agent_audit.enabled = True
    policy.checks.agent_audit.min_level = min_level
    return policy


def test_disabled_by_default_passes_without_scanning(make_pr, make_changes, policy):
    fake = _FakeScanner([AgentAuditFinding("AGENT-001", "error")])
    changes = make_changes([{"path": "a.py", "patch": "+import os", "additions": 1}])
    r = AgentAuditCheck(scanner=fake).run(make_pr(), changes, policy)
    assert r.passed and r.detail == "disabled"
    assert fake.calls == 0  # a disabled check must not run the scanner


def test_unavailable_scanner_escalates_never_fake_pass(make_pr, make_changes, policy):
    _enable(policy)
    changes = make_changes([{"path": "a.py", "patch": "+x = 1", "additions": 1}])
    r = AgentAuditCheck(scanner=_FakeScanner(None)).run(make_pr(), changes, policy)
    assert not r.passed and not r.blocking
    assert r.severity is RiskTier.MEDIUM
    assert r.evidence.get("unavailable") is True


def test_findings_at_or_above_min_level_fail_and_escalate(make_pr, make_changes, policy):
    _enable(policy, min_level="warning")
    findings = [AgentAuditFinding("AGENT-004", "error"), AgentAuditFinding("AGENT-018", "warning")]
    changes = make_changes([{"path": "a.py", "patch": "+os.system(x)", "additions": 1}])
    r = AgentAuditCheck(scanner=_FakeScanner(findings)).run(make_pr(), changes, policy)
    assert not r.passed and not r.blocking
    assert r.severity is RiskTier.HIGH  # max of error(HIGH), warning(MEDIUM)
    assert r.evidence["rule_ids"] == ["AGENT-004", "AGENT-018"]
    assert r.evidence["count"] == 2


def test_sub_threshold_findings_pass(make_pr, make_changes, policy):
    _enable(policy, min_level="warning")
    findings = [AgentAuditFinding("AGENT-020", "note")]  # below 'warning'
    changes = make_changes([{"path": "a.py", "patch": "+x = 1", "additions": 1}])
    r = AgentAuditCheck(scanner=_FakeScanner(findings)).run(make_pr(), changes, policy)
    assert r.passed and "below warning" in r.detail


def test_clean_scan_passes(make_pr, make_changes, policy):
    _enable(policy)
    changes = make_changes([{"path": "a.py", "patch": "+x = 1", "additions": 1}])
    r = AgentAuditCheck(scanner=_FakeScanner([])).run(make_pr(), changes, policy)
    assert r.passed


def test_parse_sarif_result_level_overrides_rule_default():
    sarif = """
    {"runs": [{
      "tool": {"driver": {"rules": [
        {"id": "AGENT-001", "defaultConfiguration": {"level": "warning"}}
      ]}},
      "results": [
        {"ruleId": "AGENT-001"},
        {"ruleId": "AGENT-001", "level": "error"},
        {"ruleId": "AGENT-099"}
      ]
    }]}
    """
    findings = parse_sarif(sarif)
    assert [(f.rule_id, f.level) for f in findings] == [
        ("AGENT-001", "warning"),  # falls back to rule default
        ("AGENT-001", "error"),    # result-level wins
        ("AGENT-099", "warning"),  # unknown rule -> default 'warning'
    ]


def test_subprocess_scanner_missing_binary_returns_none(make_changes):
    scanner = SubprocessAgentAuditScanner(binary="agentgate-no-such-binary-xyz")
    files = make_changes([{"path": "a.py", "patch": "+x = 1", "additions": 1}]).files
    assert scanner.scan(files) is None
