"""Combine check results (+ optional LLM review) into a single gate Decision.

Rules, in order:
  1. Any failed *blocking* check (e.g. a secret in the diff) -> REQUEST_CHANGES.
  2. Compute overall risk = max severity across failed checks and the LLM review.
  3. "No evidence => escalate": if an LLM review was expected but unavailable and
     risk >= MEDIUM, force ESCALATE (never auto-approve on missing evidence).
  4. If risk tier is in the actor's require_human_on -> ESCALATE.
  5. Else if risk <= the actor's max_auto_approve_risk -> AUTO_APPROVE.
  6. Else -> ESCALATE.
"""
from __future__ import annotations

from .domain import ActionType, CheckResult, Decision, PullRequest, RiskTier
from .policy.schema import Policy
from .review.llm_review import LLMReview


def _max_risk(tiers: list[RiskTier]) -> RiskTier:
    return max(tiers, key=lambda t: t.rank, default=RiskTier.LOW)


def decide(
    pr: PullRequest,
    check_results: list[CheckResult],
    policy: Policy,
    llm: LLMReview | None = None,
    llm_expected: bool = False,
) -> Decision:
    failed = [c for c in check_results if not c.passed]
    reasons = [f"{c.name}: {c.detail}" for c in failed]

    risk = _max_risk([c.severity for c in failed])
    if llm is not None:
        risk = _max_risk([risk, llm.risk])
        if llm.concerns:
            reasons.append("llm_review: " + "; ".join(llm.concerns))

    ap = policy.actor_policy(pr.actor.kind.value)

    # 1. hard block on blocking checks
    if any(c.blocking for c in failed):
        return Decision(action=ActionType.REQUEST_CHANGES, risk=risk, reasons=reasons,
                        check_results=check_results, llm_reviewed=llm is not None)

    # 3. no evidence => escalate
    if llm_expected and llm is None and risk.rank >= RiskTier.MEDIUM.rank:
        reasons.append("llm_review unavailable; escalating (no evidence => human)")
        return Decision(action=ActionType.ESCALATE, risk=risk, reasons=reasons,
                        check_results=check_results, llm_reviewed=False)

    # 4/5/6. actor-aware gating
    if risk in ap.require_human_on:
        action = ActionType.ESCALATE
    elif risk.rank <= ap.max_auto_approve_risk.rank:
        action = ActionType.AUTO_APPROVE
    else:
        action = ActionType.ESCALATE

    if action == ActionType.AUTO_APPROVE and not reasons:
        reasons.append("all checks passed within policy for actor")

    return Decision(action=action, risk=risk, reasons=reasons,
                    check_results=check_results, llm_reviewed=llm is not None)
