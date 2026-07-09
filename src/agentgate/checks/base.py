"""A Check is an evidence collector: given the PR + diff + policy, it returns a
CheckResult. Deterministic, no network. (Design DNA: anyagent's EvidenceCollector.)"""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain import ChangeSet, CheckResult, PullRequest
from ..policy.schema import Policy


class Check(ABC):
    name: str = "check"

    @abstractmethod
    def run(self, pr: PullRequest, changes: ChangeSet, policy: Policy) -> CheckResult: ...
