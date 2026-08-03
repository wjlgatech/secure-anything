from __future__ import annotations

import pytest
from sqlalchemy.orm import sessionmaker

from secure_anything.organs.agentgate.db import init_db, make_engine
from secure_anything.organs.agentgate.domain import (
    Actor,
    ActorKind,
    ChangeSet,
    FileChange,
    PullRequest,
)
from secure_anything.organs.agentgate.policy import DEFAULT_POLICY_PATH
from secure_anything.organs.agentgate.policy.engine import load_policy


@pytest.fixture
def policy():
    return load_policy(DEFAULT_POLICY_PATH)


@pytest.fixture
def make_pr():
    def _make(kind: ActorKind = ActorKind.HUMAN, login: str = "alice", number: int = 1,
              delivery_id: str = "d1") -> PullRequest:
        return PullRequest(
            repo="octo/repo", number=number, title="t", actor=Actor(login=login, kind=kind),
            delivery_id=delivery_id,
        )
    return _make


@pytest.fixture
def make_changes():
    def _make(files: list[dict]) -> ChangeSet:
        return ChangeSet(files=[FileChange(**f) for f in files])
    return _make


@pytest.fixture
def session():
    eng = make_engine("sqlite:///:memory:")
    init_db(eng)
    Session = sessionmaker(bind=eng, future=True, expire_on_commit=False)
    with Session() as s:
        yield s
