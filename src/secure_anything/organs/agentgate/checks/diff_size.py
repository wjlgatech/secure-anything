from __future__ import annotations

from ..domain import ChangeSet, CheckResult, PullRequest, RiskTier
from ..policy.schema import Policy
from .base import Check


class DiffSizeCheck(Check):
    name = "diff_size"

    def run(self, pr: PullRequest, changes: ChangeSet, policy: Policy) -> CheckResult:
        cfg = policy.checks.diff_size
        churn = changes.total_churn
        ev = {"total_churn": churn, "files": len(changes.files)}
        if churn > cfg.hard_max_churn:
            return CheckResult(
                name=self.name, passed=False, severity=RiskTier.HIGH,
                detail=f"{churn} changed lines exceeds hard limit {cfg.hard_max_churn}",
                evidence=ev,
            )
        if churn > cfg.max_churn:
            return CheckResult(
                name=self.name, passed=False, severity=RiskTier.MEDIUM,
                detail=f"{churn} changed lines exceeds {cfg.max_churn}",
                evidence=ev,
            )
        return CheckResult(name=self.name, passed=True, detail=f"{churn} changed lines", evidence=ev)
