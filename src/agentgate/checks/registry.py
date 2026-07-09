from __future__ import annotations

from .base import Check
from .diff_size import DiffSizeCheck
from .secret_scan import SecretScanCheck
from .touched_paths import TouchedPathsCheck


def default_checks() -> list[Check]:
    """The deterministic checks run on every PR, in order."""
    return [SecretScanCheck(), TouchedPathsCheck(), DiffSizeCheck()]
