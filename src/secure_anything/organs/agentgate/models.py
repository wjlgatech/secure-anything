"""AgentGate organ ORM models. The ledger tables are CORE-owned (secure_anything.store);
this module adds only the organ's own PR-review record and re-exports the core Base."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ...store import AuditEvent, Base, utcnow  # noqa: F401  (re-exported for the organ)




class PRReview(Base):
    """The outcome record for one PR delivery (idempotent on delivery_id)."""

    __tablename__ = "pr_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    delivery_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    repo: Mapped[str] = mapped_column(String(255), index=True)
    number: Mapped[int] = mapped_column(Integer, index=True)
    actor_login: Mapped[str] = mapped_column(String(255))
    actor_kind: Mapped[str] = mapped_column(String(32))
    action: Mapped[str] = mapped_column(String(32))
    risk: Mapped[str] = mapped_column(String(16))
    reasons: Mapped[str] = mapped_column(Text, default="")
