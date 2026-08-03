"""Persistence base for the ledger. Core-owned so no organ owns the record."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Engine, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class AuditEvent(Base):
    """Append-only, hash-chained. Each row's `hash` covers the previous row's hash,
    so any tampering with history is detectable by re-walking the chain."""

    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    kind: Mapped[str] = mapped_column(String(64))
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64), unique=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    # Ed25519 signature over `hash` (base64), when a signer is configured (ADR-003).
    # Nullable: an unsigned chain (signer=None) leaves this NULL and verifies as before.
    signature: Mapped[str | None] = mapped_column(String(128), nullable=True, default=None)


def make_engine(url: str) -> Engine:
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args, future=True)


def init_db(engine: Engine) -> None:
    """Create the ledger tables. Core-owned: the record must be testable with no organ."""
    Base.metadata.create_all(engine)
