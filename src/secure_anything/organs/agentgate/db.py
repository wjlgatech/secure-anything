"""Database engine/session wiring. Postgres in prod; SQLite for dev/tests."""
from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from ...store import init_db, make_engine  # noqa: F401  (core-owned, re-exported)
from .config import get_settings


_engine: Engine | None = None
_Session: sessionmaker[Session] | None = None


def engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = make_engine(get_settings().database_url)
        init_db(_engine)
    return _engine


def session_factory() -> sessionmaker[Session]:
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=engine(), future=True, expire_on_commit=False)
    return _Session
