from secure_anything.organs.agentgate.actor import classify_actor
from secure_anything.organs.agentgate.domain import ActorKind

AGENTS = ["claude", "cursor", "devin", "copilot"]


def test_human():
    a = classify_actor("alice", "User", AGENTS)
    assert a.kind is ActorKind.HUMAN


def test_ai_agent_by_slug():
    a = classify_actor("claude-code[bot]", "Bot", AGENTS)
    assert a.kind is ActorKind.AI_AGENT
    assert a.label == "claude-code"


def test_ai_agent_user_login():
    # some agents author as plain Users
    a = classify_actor("cursor-agent", "User", AGENTS)
    assert a.kind is ActorKind.AI_AGENT


def test_plain_bot_is_not_agent():
    a = classify_actor("dependabot[bot]", "Bot", AGENTS)
    assert a.kind is ActorKind.BOT
