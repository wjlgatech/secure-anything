"""Core runtime types shared across the pipeline (pure data, no I/O)."""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ActorKind(str, Enum):
    HUMAN = "human"
    AI_AGENT = "ai_agent"
    BOT = "bot"  # non-agent automation (dependabot, CI bots)


class RiskTier(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2}[self.value]


class ActionType(str, Enum):
    AUTO_APPROVE = "auto_approve"
    REQUEST_CHANGES = "request_changes"
    ESCALATE = "escalate_to_human"  # route to a human approver


class Actor(BaseModel):
    login: str
    kind: ActorKind
    label: str = ""  # e.g. "claude-code", "cursor-agent", "dependabot"


class FileChange(BaseModel):
    path: str
    additions: int = 0
    deletions: int = 0
    patch: str = ""  # unified diff hunk, when available

    @property
    def churn(self) -> int:
        return self.additions + self.deletions


class ChangeSet(BaseModel):
    files: list[FileChange] = Field(default_factory=list)

    @property
    def total_churn(self) -> int:
        return sum(f.churn for f in self.files)

    @property
    def paths(self) -> list[str]:
        return [f.path for f in self.files]


class PullRequest(BaseModel):
    repo: str  # "owner/name"
    number: int
    title: str = ""
    body: str = ""
    head_sha: str = ""
    actor: Actor
    delivery_id: str = ""  # webhook delivery id, for idempotency + audit


class CheckResult(BaseModel):
    name: str
    passed: bool
    severity: RiskTier = RiskTier.LOW  # severity IF failed
    blocking: bool = False  # if failed, hard-block (request changes) rather than escalate
    detail: str = ""
    evidence: dict = Field(default_factory=dict)


class Decision(BaseModel):
    action: ActionType
    risk: RiskTier
    reasons: list[str] = Field(default_factory=list)
    check_results: list[CheckResult] = Field(default_factory=list)
    llm_reviewed: bool = False
