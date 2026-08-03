"""Fixtures for the public tree — core only, no organ required.

The ledger is core-owned, so its tests must run with nothing but `secure_anything`.
"""
from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker

from secure_anything.store import init_db, make_engine


@pytest.fixture
def session():
    eng = make_engine("sqlite:///:memory:")
    init_db(eng)
    Session = sessionmaker(bind=eng, future=True, expire_on_commit=False)
    with Session() as s:
        yield s
