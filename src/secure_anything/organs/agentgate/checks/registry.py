from __future__ import annotations

from .agent_audit import AgentAuditCheck
from .base import Check
from .diff_size import DiffSizeCheck
from .secret_scan import SecretScanCheck
from .touched_paths import TouchedPathsCheck


def default_checks() -> list[Check]:
    """The deterministic checks run on every PR, in order. `agent_audit` is opt-in
    (disabled in policy by default) so it's a no-op until an operator enables it."""
    return [SecretScanCheck(), TouchedPathsCheck(), DiffSizeCheck(), AgentAuditCheck()]
