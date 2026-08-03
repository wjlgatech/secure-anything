from secure_anything.ledger import GENESIS, AuditLedger, verify_chain
from secure_anything.store import AuditEvent


def test_chain_appends_and_verifies(session):
    ledger = AuditLedger(session)
    assert ledger.latest_hash() == GENESIS
    e1 = ledger.append("pr_decision", {"repo": "o/r", "number": 1, "action": "auto_approve"})
    e2 = ledger.append("pr_decision", {"repo": "o/r", "number": 2, "action": "escalate_to_human"})
    assert e1.prev_hash == GENESIS
    assert e2.prev_hash == e1.hash
    assert ledger.verify() is True


def test_tamper_is_detected(session):
    ledger = AuditLedger(session)
    ledger.append("pr_decision", {"repo": "o/r", "number": 1, "action": "auto_approve"})
    ledger.append("pr_decision", {"repo": "o/r", "number": 2, "action": "auto_approve"})
    # someone edits history to hide a decision
    row = session.query(AuditEvent).order_by(AuditEvent.id.asc()).first()
    row.payload = {"repo": "o/r", "number": 1, "action": "escalate_to_human"}
    session.commit()
    assert ledger.verify() is False


def test_verify_chain_pure():
    assert verify_chain([]) is True
