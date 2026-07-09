"""Classify who authored a PR: a human, an AI coding agent, or plain automation.

This is the heart of "for human + AI agents" — the gate applies different policy
depending on the author kind (agents are held to a stricter bar by default).
"""
from __future__ import annotations

from .domain import Actor, ActorKind


def classify_actor(login: str, gh_type: str, agent_identities: list[str]) -> Actor:
    """Map a GitHub author to an Actor.

    - gh_type is GitHub's own field: "User" or "Bot".
    - agent_identities is a policy-provided list of substrings/slugs that mark an
      author as an AI coding agent (e.g. "claude", "cursor", "devin", "copilot").
    """
    login_l = (login or "").lower()
    slug = login_l.removesuffix("[bot]")

    is_agent = any(ident.lower() in slug for ident in agent_identities)
    if is_agent:
        return Actor(login=login, kind=ActorKind.AI_AGENT, label=slug)

    if gh_type == "Bot" or login_l.endswith("[bot]"):
        return Actor(login=login, kind=ActorKind.BOT, label=slug)

    return Actor(login=login, kind=ActorKind.HUMAN, label=login_l)
