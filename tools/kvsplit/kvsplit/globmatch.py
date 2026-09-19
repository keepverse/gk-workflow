"""Git-style path globs compiled to anchored regular expressions.

Supported syntax, deliberately small so a rule means exactly one thing:
  **   any number of path segments (including none)
  *    any characters except '/'
  ?    one character except '/'
Everything else is literal. Paths are repo-relative, '/'-separated, case-sensitive.
"""

from __future__ import annotations

import re
from functools import lru_cache


@lru_cache(maxsize=None)
def compile_glob(pattern: str) -> re.Pattern[str]:
    if not pattern or pattern.startswith("/") or "\\" in pattern:
        raise ValueError(f"invalid glob {pattern!r}: must be non-empty, repo-relative, '/'-separated")
    out: list[str] = []
    i = 0
    n = len(pattern)
    while i < n:
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("/**", i) and i + 3 == n:
            out.append("(?:/.*)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out) + r"\Z")


def matches(pattern: str, path: str) -> bool:
    return compile_glob(pattern).match(path) is not None
