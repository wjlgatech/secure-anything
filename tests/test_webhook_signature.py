import hashlib
import hmac

from secure_anything.organs.agentgate.webhooks.github import (
    parse_pull_request_event,
    verify_signature,
)

SECRET = "s3cr3t-webhook-key"


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


def test_valid_signature():
    body = b'{"hello":"world"}'
    assert verify_signature(SECRET, body, _sign(body)) is True


def test_tampered_body_rejected():
    body = b'{"hello":"world"}'
    sig = _sign(body)
    assert verify_signature(SECRET, b'{"hello":"evil"}', sig) is False


def test_missing_or_malformed_signature():
    assert verify_signature(SECRET, b"x", None) is False
    assert verify_signature(SECRET, b"x", "md5=deadbeef") is False
    assert verify_signature("", b"x", "sha256=abc") is False


def test_parse_pull_request_event(policy):
    payload = {
        "action": "opened",
        "repository": {"full_name": "octo/repo"},
        "pull_request": {
            "number": 7, "title": "add feature", "body": "",
            "user": {"login": "claude-code[bot]", "type": "Bot"},
            "head": {"sha": "abc123"},
        },
    }
    pr = parse_pull_request_event(payload, policy, delivery_id="dlv-1")
    assert pr is not None
    assert pr.repo == "octo/repo" and pr.number == 7
    assert pr.actor.kind.value == "ai_agent"
    assert pr.delivery_id == "dlv-1"


def test_parse_ignores_uninteresting_actions(policy):
    assert parse_pull_request_event({"action": "labeled"}, policy) is None
