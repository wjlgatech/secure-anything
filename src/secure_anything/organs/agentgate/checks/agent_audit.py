"""Run the `agent-audit` SAST (OWASP Agentic Top-10 static scanner, USC FORTIS Lab)
over the PR's added diff content as an evidence collector.

Opt-in: it needs the external `agent-audit` tool (`pip install agent-audit`), so it
is disabled by default. The scanner is an INJECTABLE SEAM — the check stays
offline-deterministic in tests (inject a fake), while the default body shells out to
`agent-audit scan ... --format sarif`. (Design DNA: anyagent's EvidenceCollector +
AgentGate's "no evidence => escalate, never a fake pass".)

Honesty rules:
  - disabled in policy            -> pass (explicitly opted out)
  - enabled but tool unavailable  -> non-blocking fail at MEDIUM ("no evidence =>
                                     human"). Never a fake pass. Note the actor-aware
                                     consequence: an AI agent escalates on MEDIUM,
                                     a human (trusted at medium) may still auto-merge.
  - findings >= min_level         -> non-blocking fail at the max mapped severity
                                     (routes to a human), evidence = rule ids
  - only sub-threshold findings   -> pass

Scope limit: the default scanner sees ADDED diff content only (new code the PR
introduces), NOT a full checkout — so cross-file taint flows through unchanged files
are out of scope. Inject a full-checkout scanner to widen coverage later.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..domain import ChangeSet, CheckResult, FileChange, PullRequest, RiskTier
from ..policy.schema import Policy
from .base import Check

# SARIF level -> our risk tier (agent-audit maps CRITICAL/HIGH->error, MEDIUM->warning,
# LOW->note, INFO->none, per its sarif formatter).
_LEVEL_TO_TIER = {
    "error": RiskTier.HIGH,
    "warning": RiskTier.MEDIUM,
    "note": RiskTier.LOW,
    "none": RiskTier.LOW,
}
_LEVEL_RANK = {"none": 0, "note": 0, "warning": 1, "error": 2}


@dataclass(frozen=True)
class AgentAuditFinding:
    rule_id: str
    level: str  # SARIF level: error | warning | note | none


class AgentAuditScanner(Protocol):
    """Returns findings, [] for a clean scan, or None if it could not run at all
    (tool missing / crashed) — None is the 'no evidence' signal, not a clean pass."""

    def scan(self, files: list[FileChange]) -> list[AgentAuditFinding] | None: ...


def _added_content(f: FileChange) -> str:
    lines = [
        ln[1:]
        for ln in f.patch.splitlines()
        if ln.startswith("+") and not ln.startswith("+++")
    ]
    return "\n".join(lines)


def parse_sarif(text: str) -> list[AgentAuditFinding]:
    """Extract (rule_id, level) per result. A result's own `level` wins; otherwise
    fall back to the rule's defaultConfiguration.level; otherwise 'warning'."""
    data = json.loads(text)
    findings: list[AgentAuditFinding] = []
    for run in data.get("runs", []):
        rule_level: dict[str, str] = {}
        for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
            lvl = rule.get("defaultConfiguration", {}).get("level")
            if rule.get("id") and lvl:
                rule_level[rule["id"]] = lvl
        for res in run.get("results", []):
            rid = res.get("ruleId", "")
            level = res.get("level") or rule_level.get(rid, "warning")
            findings.append(AgentAuditFinding(rule_id=rid, level=level))
    return findings


class SubprocessAgentAuditScanner:
    """Default body: write the PR's added content to a temp tree and run
    `agent-audit scan <dir> --format sarif --output <file>`. Fully guarded — any
    failure (tool absent, crash, unreadable output) returns None so the check
    escalates rather than fabricating a pass."""

    def __init__(self, binary: str = "agent-audit", timeout: int = 120) -> None:
        self.binary = binary
        self.timeout = timeout

    def scan(self, files: list[FileChange]) -> list[AgentAuditFinding] | None:
        if shutil.which(self.binary) is None:
            return None
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                wrote = False
                for f in files:
                    content = _added_content(f)
                    if not content:
                        continue
                    dest = root / f.path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(content)
                    wrote = True
                if not wrote:
                    return []  # nothing new to scan => no findings
                out = root / "_agentgate_agent_audit.sarif"
                # agent-audit exits non-zero when findings exist (--fail-on); that is
                # NOT a runner error, so we key off the output file, not returncode.
                subprocess.run(
                    [self.binary, "scan", str(root),
                     "--format", "sarif", "--output", str(out)],
                    capture_output=True, text=True, timeout=self.timeout,
                )
                if not out.exists():
                    return None
                return parse_sarif(out.read_text())
        except Exception:
            return None


class AgentAuditCheck(Check):
    name = "agent_audit"

    def __init__(self, scanner: AgentAuditScanner | None = None) -> None:
        # Constructing the default scanner is cheap and side-effect-free; the
        # subprocess only fires inside .scan(), and only when the check is enabled.
        self._scanner: AgentAuditScanner = scanner or SubprocessAgentAuditScanner()

    def run(self, pr: PullRequest, changes: ChangeSet, policy: Policy) -> CheckResult:
        cfg = policy.checks.agent_audit
        if not cfg.enabled:
            return CheckResult(name=self.name, passed=True, detail="disabled")

        findings = self._scanner.scan(changes.files)
        if findings is None:
            return CheckResult(
                name=self.name, passed=False, severity=RiskTier.MEDIUM, blocking=False,
                detail="agent-audit unavailable; escalating (no evidence => human)",
                evidence={"unavailable": True},
            )

        min_rank = _LEVEL_RANK.get(cfg.min_level, 1)
        relevant = [f for f in findings if _LEVEL_RANK.get(f.level, 1) >= min_rank]
        if not relevant:
            return CheckResult(
                name=self.name, passed=True,
                detail=f"agent-audit clean ({len(findings)} finding(s) below {cfg.min_level})",
            )

        severity = max(
            (_LEVEL_TO_TIER.get(f.level, RiskTier.LOW) for f in relevant),
            key=lambda t: t.rank,
        )
        rule_ids = sorted({f.rule_id for f in relevant if f.rule_id})
        return CheckResult(
            name=self.name, passed=False, severity=severity, blocking=False,
            detail=f"agent-audit: {len(relevant)} finding(s) >= {cfg.min_level}: "
                   f"{', '.join(rule_ids)}",
            evidence={"rule_ids": rule_ids, "count": len(relevant)},
        )
