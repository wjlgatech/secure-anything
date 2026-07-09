"""Job queue abstraction. In-process deque by default (dev); Redis for scale-out
so the API stays snappy under a burst of 50 agents opening PRs at once."""
from __future__ import annotations

import json
from collections import deque
from typing import Protocol

from .config import Settings


class Queue(Protocol):
    def enqueue(self, job: dict) -> None: ...
    def dequeue(self) -> dict | None: ...


class InMemoryQueue:
    def __init__(self) -> None:
        self._q: deque[dict] = deque()

    def enqueue(self, job: dict) -> None:
        self._q.append(job)

    def dequeue(self) -> dict | None:
        return self._q.popleft() if self._q else None


class RedisQueue:
    KEY = "agentgate:jobs"

    def __init__(self, url: str) -> None:
        import redis  # optional dependency; only imported when selected

        self._r = redis.Redis.from_url(url)

    def enqueue(self, job: dict) -> None:
        self._r.rpush(self.KEY, json.dumps(job))

    def dequeue(self) -> dict | None:
        raw = self._r.lpop(self.KEY)
        return json.loads(raw) if raw else None


_singleton: Queue | None = None


def get_queue(settings: Settings) -> Queue:
    global _singleton
    if _singleton is None:
        _singleton = (
            RedisQueue(settings.redis_url)
            if settings.queue_backend == "redis"
            else InMemoryQueue()
        )
    return _singleton
