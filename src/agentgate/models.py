"""SQLAlchemy ORM models: the audit ledger and PR review records."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class AuditEvent(Base):
    """Append-only, hash-chained. Each row's `hash` covers the previous row's hash,
    so any tampering with history is detectable by re-walking the chain."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    kind: Mapped[str] = mapped_column(String(64))
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64), unique=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    # Ed25519 signature over `hash` (base64), when a signer is configured (ADR-003).
    # Nullable: an unsigned chain (signer=None) leaves this NULL and verifies as before.
    signature: Mapped[str | None] = mapped_column(String(128), nullable=True, default=None)


class PRReview(Base):
    """The outcome record for one PR delivery (idempotent on delivery_id)."""

    __tablename__ = "pr_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    delivery_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    repo: Mapped[str] = mapped_column(String(255), index=True)
    number: Mapped[int] = mapped_column(Integer, index=True)
    actor_login: Mapped[str] = mapped_column(String(255))
    actor_kind: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(32))
    risk: Mapped[str] = mapped_column(String(16))
    reasons: Mapped[str] = mapped_column(Text, default="")
