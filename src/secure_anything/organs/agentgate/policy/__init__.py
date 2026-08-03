"""Policy is DATA, not prompt. The default document ships with the organ."""
from pathlib import Path

# Resolved from __file__, never from the CWD: a directory move must not silently
# swap in a different policy. (Earned 2026-08-03 — the organ move broke four tests
# because three call sites hardcoded the old string path.)
DEFAULT_POLICY_PATH = Path(__file__).with_name("default_policy.yaml")
