"""Tamper-evident audit ledger.

Every consequential event (a decision, an approval, an override) is appended as a
hash-chained record: hash = sha256(prev_hash | kind | canonical(payload)). Re-walking
the chain detects any insertion, deletion, or edit of history. This is what turns
"the agent did X" into court/compliance-grade evidence (EU AI Act, FINRA auditability).
"""
from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session

from .store import AuditEvent

if TYPE_CHECKING:
    from .signing import Signer

GENESIS = "0" * 64


def canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(prev_hash: str, kind: str, payload: dict) -> str:
    material = f"{prev_hash}|{kind}|{canonical(payload)}".encode()
    return hashlib.sha256(material).hexdigest()


class AuditLedger:
    def __init__(self, session: Session, signer: Signer | None = None):
        self.session = session
        # Optional Ed25519 signer (ADR-003). When set, each chain head is signed so
        # tampering is detectable even against an operator who can rewrite the DB.
        self.signer = signer

    def latest_hash(self) -> str:
        row = self.session.execute(
            select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)
        ).scalar_one_or_none()
        return row.hash if row else GENESIS

    def append(self, kind: str, payload: dict) -> AuditEvent:
        prev = self.latest_hash()
        h = compute_hash(prev, kind, payload)
        signature = self.signer.sign(h.encode()) if self.signer else None
        event = AuditEvent(kind=kind, prev_hash=prev, hash=h, payload=payload,
                           signature=signature)
        self.session.add(event)
        self.session.commit()
        return event

    def verify(self) -> bool:
        events = self.session.execute(
            select(AuditEvent).order_by(AuditEvent.id.asc())
        ).scalars().all()
        return verify_chain(events, signer=self.signer)


def verify_chain(events: list[AuditEvent], signer: Signer | None = None) -> bool:
    """Chain integrity, plus signature authenticity when a signer is supplied.
    With a signer, every event MUST carry a signature valid for its hash — an
    unsigned row in a signed ledger is treated as tampering (a dropped signature)."""
    prev = GENESIS
    for e in events:
        if e.prev_hash != prev:
            return False
        if e.hash != compute_hash(e.prev_hash, e.kind, e.payload):
            return False
        if signer is not None:
            if not e.signature or not signer.verify(e.hash.encode(), e.signature):
                return False
        prev = e.hash
    return True
