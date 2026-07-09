from __future__ import annotations

from ..domain import ChangeSet, CheckResult, PullRequest
from ..policy.schema import Policy
from .base import Check
from .paths import path_matches


class TouchedPathsCheck(Check):
    name = "touched_paths"

    def run(self, pr: PullRequest, changes: ChangeSet, policy: Policy) -> CheckResult:
        cfg = policy.checks.touched_paths
        hits = [
            path for path in changes.paths
            if any(path_matches(path, pat) for pat in cfg.protected)
        ]
        if hits:
            return CheckResult(
                name=self.name, passed=False, severity=cfg.severity,
                detail=f"touches protected path(s): {', '.join(hits)}",
                evidence={"protected_hits": hits},
            )
        return CheckResult(name=self.name, passed=True, detail="no protected paths touched")
