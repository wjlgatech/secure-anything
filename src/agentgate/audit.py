"""Tamper-evident audit ledger.

Every consequential event (a decision, an approval, an override) is appended as a
hash-chained record: hash = sha256(prev_hash | kind | canonical(payload)). Re-walking
the chain detects any insertion, deletion, or edit of history. This is what turns
"the agent did X" into court/compliance-grade evidence (EU AI Act, FINRA auditability).
"""
from __future__ import annotations

import hashlib
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditEvent

GENESIS = "0" * 64


def canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def compute_hash(prev_hash: str, kind: str, payload: dict) -> str:
    material = f"{prev_hash}|{kind}|{canonical(payload)}".encode()
    return hashlib.sha256(material).hexdigest()


class AuditLedger:
    def __init__(self, session: Session):
        self.session = session

    def latest_hash(self) -> str:
        row = self.session.execute(
            select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)
        ).scalar_one_or_none()
        return row.hash if row else GENESIS

    def append(self, kind: str, payload: dict) -> AuditEvent:
        prev = self.latest_hash()
        h = compute_hash(prev, kind, payload)
        event = AuditEvent(kind=kind, prev_hash=prev, hash=h, payload=payload)
        self.session.add(event)
        self.session.commit()
        return event

    def verify(self) -> bool:
        events = self.session.execute(
            select(AuditEvent).order_by(AuditEvent.id.asc())
        ).scalars().all()
        return verify_chain(events)


def verify_chain(events: list[AuditEvent]) -> bool:
    prev = GENESIS
    for e in events:
        if e.prev_hash != prev:
            return False
        if e.hash != compute_hash(e.prev_hash, e.kind, e.payload):
            return False
        prev = e.hash
    return True
