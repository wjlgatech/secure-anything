"""secure-anything — the composition layer for agent security.

A meta-package: it owns no domain logic. It holds a registry of capabilities, a
deterministic router, a uniform gate seam, and a tamper-evident ledger. Domain work
lives in `organs/` (ours) or upstream satellites (theirs). See docs/VISION.md.
"""

__version__ = "0.2.0"
