"""Load and cache the policy document."""
from __future__ import annotations

from pathlib import Path

import yaml

from .schema import Policy


def load_policy(path: str | Path) -> Policy:
    p = Path(path)
    if not p.exists():
        # A missing policy must not silently allow everything. `Policy()` would do exactly
        # that (no protected paths => LOW risk => agent auto-approve), so fall back to the
        # explicit deny-by-default posture instead. See ADR-004.
        return Policy.strict()
    data = yaml.safe_load(p.read_text()) or {}
    return Policy.model_validate(data)
