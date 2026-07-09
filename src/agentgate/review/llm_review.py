"""Optional LLM risk review — a pluggable seam.

If no API key is configured, `review()` returns None (unavailable). The decision
engine then applies "no evidence => escalate" for risky diffs rather than faking a
pass. This keeps the gate honest when the reviewer can't run.
"""
from __future__ import annotations

from pydantic import BaseModel

from ..config import Settings
from ..domain import ChangeSet, PullRequest, RiskTier


class LLMReview(BaseModel):
    risk: RiskTier
    summary: str
    concerns: list[str] = []


def review(pr: PullRequest, changes: ChangeSet, settings: Settings) -> LLMReview | None:
    """Return an LLM risk assessment, or None if the reviewer is unavailable.

    The real implementation calls the Claude API (settings.llm_model) with the diff
    and a rubric, returning structured JSON. It is intentionally gated behind a key
    so tests and dev run fully offline and deterministically.
    """
    if not settings.llm_review_enabled:
        return None
    # NOTE: live call intentionally omitted from the open MVP; wire the Anthropic
    # SDK here. Must return an LLMReview or raise (worker treats a raised/None as
    # "unavailable" -> escalate on risk).
    raise NotImplementedError("LLM review requires the Anthropic client to be wired in")
