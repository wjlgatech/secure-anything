"""Policy is DATA, not prompt. A jailbroken agent can't argue its way past a YAML
file. This is the single source of truth the decision engine enforces."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..domain import RiskTier


class DiffSizeConfig(BaseModel):
    max_churn: int = 800  # added+deleted lines above this => medium-risk fail
    hard_max_churn: int = 3000  # above this => high-risk fail


class SecretScanConfig(BaseModel):
    enabled: bool = True


class TouchedPathsConfig(BaseModel):
    protected: list[str] = Field(default_factory=list)  # glob patterns
    severity: RiskTier = RiskTier.HIGH


class AgentAuditConfig(BaseModel):
    enabled: bool = False        # opt-in: needs the external `agent-audit` SAST tool
    min_level: str = "warning"   # ignore SARIF findings below this: note | warning | error


class ChecksConfig(BaseModel):
    diff_size: DiffSizeConfig = Field(default_factory=DiffSizeConfig)
    secret_scan: SecretScanConfig = Field(default_factory=SecretScanConfig)
    touched_paths: TouchedPathsConfig = Field(default_factory=TouchedPathsConfig)
    agent_audit: AgentAuditConfig = Field(default_factory=AgentAuditConfig)


class ActorPolicy(BaseModel):
    # Highest risk tier this actor kind may have AUTO-APPROVED.
    max_auto_approve_risk: RiskTier = RiskTier.LOW
    # Risk tiers that MUST route to a human, regardless of anything else.
    require_human_on: list[RiskTier] = Field(default_factory=lambda: [RiskTier.HIGH])


class Policy(BaseModel):
    version: str = "0.1"
    agent_identities: list[str] = Field(default_factory=list)
    checks: ChecksConfig = Field(default_factory=ChecksConfig)
    actors: dict[str, ActorPolicy] = Field(default_factory=dict)

    @classmethod
    def strict(cls) -> "Policy":
        """Deny-by-default posture, used when no policy document could be loaded.

        A bare `Policy()` is NOT strict — it protects no paths, so every check passes,
        risk lands at LOW, and an AI-agent PR AUTO-APPROVES. That is fail-open and
        contradicts ADR-002. This constructor routes every risk tier to a human, so a
        missing policy file blocks merges instead of waving them through.
        (Found 2026-08-03 while moving the organ; see ADR-004.)
        """
        every = [RiskTier.LOW, RiskTier.MEDIUM, RiskTier.HIGH]
        return cls(
            actors={
                kind: ActorPolicy(max_auto_approve_risk=RiskTier.LOW, require_human_on=every)
                for kind in ("human", "ai_agent", "bot")
            }
        )

    def actor_policy(self, kind: str) -> ActorPolicy:
        # Default to the strictest posture if a kind is unspecified.
        return self.actors.get(
            kind,
            ActorPolicy(max_auto_approve_risk=RiskTier.LOW, require_human_on=[RiskTier.HIGH]),
        )
