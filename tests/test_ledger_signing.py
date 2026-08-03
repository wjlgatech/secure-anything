"""Ed25519 audit-ledger signing (ADR-003). Deterministic + offline: keys are
generated in-memory, sign/verify run on bytes — no network, no disk."""
from __future__ import annotations

import pytest

from secure_anything.ledger import AuditLedger, verify_chain
from secure_anything.store import AuditEvent

pytest.importorskip("cryptography")
from secure_anything.signing import Ed25519Signer


def test_sign_and_verify_roundtrip():
    signer = Ed25519Signer()
    sig = signer.sign(b"hello")
    assert signer.verify(b"hello", sig) is True
    assert signer.verify(b"tampered", sig) is False
    assert len(signer.public_key_hex()) == 64  # 32-byte raw key, hex


def test_signed_ledger_appends_signature_and_verifies(session):
    ledger = AuditLedger(session, signer=Ed25519Signer())
    e1 = ledger.append("pr_decision", {"n": 1})
    e2 = ledger.append("pr_decision", {"n": 2})
    assert e1.signature and e2.signature
    assert ledger.verify() is True


def test_signature_tamper_is_detected(session):
    signer = Ed25519Signer()
    ledger = AuditLedger(session, signer=signer)
    ledger.append("pr_decision", {"n": 1})
    ledger.append("pr_decision", {"n": 2})

    # An operator rewrites a row AND recomputes the hash chain to stay internally
    # consistent — plain hash-chaining would miss this. The signature will not match.
    from secure_anything.ledger import compute_hash

    rows = session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
    rows[0].payload = {"n": 99}
    rows[0].hash = compute_hash(rows[0].prev_hash, rows[0].kind, rows[0].payload)
    rows[1].prev_hash = rows[0].hash
    rows[1].hash = compute_hash(rows[1].prev_hash, rows[1].kind, rows[1].payload)
    session.commit()

    # Chain-only verification is fooled; signature verification catches it.
    assert verify_chain(rows) is True                 # internally consistent again
    assert verify_chain(rows, signer=signer) is False  # signatures no longer match
    assert ledger.verify() is False


def test_dropped_signature_in_signed_ledger_is_tampering(session):
    signer = Ed25519Signer()
    ledger = AuditLedger(session, signer=signer)
    ledger.append("pr_decision", {"n": 1})
    row = session.query(AuditEvent).first()
    row.signature = None
    session.commit()
    assert ledger.verify() is False


def test_wrong_key_fails_verification(session):
    ledger = AuditLedger(session, signer=Ed25519Signer())
    ledger.append("pr_decision", {"n": 1})
    rows = session.query(AuditEvent).order_by(AuditEvent.id.asc()).all()
    assert verify_chain(rows, signer=Ed25519Signer()) is False  # a different key


def test_unsigned_ledger_still_works(session):
    # signer=None => behaves exactly as the original hash-chain (backward compatible)
    ledger = AuditLedger(session)
    ledger.append("pr_decision", {"n": 1})
    assert ledger.verify() is True


def test_key_save_load_roundtrip(tmp_path):
    signer = Ed25519Signer()
    sig = signer.sign(b"m")
    path = tmp_path / "audit_key.pem"
    signer.save_private_key(path)
    assert (path.stat().st_mode & 0o777) == 0o600
    loaded = Ed25519Signer.load(path)
    assert loaded.verify(b"m", sig) is True
    assert loaded.public_key_hex() == signer.public_key_hex()
