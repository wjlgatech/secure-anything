"""Load and cache the policy document."""
from __future__ import annotations

from pathlib import Path

import yaml

from .schema import Policy


def load_policy(path: str | Path) -> Policy:
    p = Path(path)
    if not p.exists():
        # A missing policy must not silently allow everything — fall back to the
        # strictest built-in defaults (every risk tier requires a human).
        return Policy()
    data = yaml.safe_load(p.read_text()) or {}
    return Policy.model_validate(data)
