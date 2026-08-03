"""Glob matching for touched-path rules. fnmatch's `*` spans `/`, so we normalise
`**` to `*` and also allow a `**/` prefix to match zero directories."""
from __future__ import annotations

from fnmatch import fnmatch


def path_matches(path: str, pattern: str) -> bool:
    normalized = pattern.replace("**", "*")
    if fnmatch(path, normalized):
        return True
    # allow "**/x" to also match a root-level "x"
    if "*/" in normalized and fnmatch(path, normalized.replace("*/", "", 1)):
        return True
    return False
