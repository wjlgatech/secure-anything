"""Scan ADDED diff lines for hardcoded secrets. Deterministic regex set; a hit is
a hard block (request changes), not merely an escalation."""
from __future__ import annotations

import re

from ..domain import ChangeSet, CheckResult, PullRequest, RiskTier
from ..policy.schema import Policy
from .base import Check

SECRET_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("generic_secret", re.compile(
        r"(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"
    )),
]


def _added_lines(changes: ChangeSet) -> list[str]:
    lines: list[str] = []
    for f in changes.files:
        for ln in f.patch.splitlines():
            if ln.startswith("+") and not ln.startswith("+++"):
                lines.append(ln[1:])
    return lines


class SecretScanCheck(Check):
    name = "secret_scan"

    def run(self, pr: PullRequest, changes: ChangeSet, policy: Policy) -> CheckResult:
        if not policy.checks.secret_scan.enabled:
            return CheckResult(name=self.name, passed=True, detail="disabled")
        hits: list[str] = []
        for line in _added_lines(changes):
            for label, pat in SECRET_PATTERNS:
                if pat.search(line):
                    hits.append(label)
        if hits:
            return CheckResult(
                name=self.name, passed=False, severity=RiskTier.HIGH, blocking=True,
                detail=f"possible secret(s) in diff: {', '.join(sorted(set(hits)))}",
                evidence={"kinds": sorted(set(hits))},
            )
        return CheckResult(name=self.name, passed=True, detail="no secrets detected")
