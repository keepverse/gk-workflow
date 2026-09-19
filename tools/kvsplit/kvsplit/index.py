"""The path index of a moved workspace: every file that exists now, plus the old -> new move map.

Built from the moved workspace (what is really there) and report.json (where each legacy file went).
The reindex step resolves document references against it; it is also reusable for any later move by
supplying a different old -> new map.
"""

from __future__ import annotations

import bisect
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathIndex:
    files: list[str]                 # sorted workspace paths that exist
    moves: dict[str, str]            # legacy path -> primary workspace path

    def __post_init__(self) -> None:
        self.files = sorted(self.files)
        self._file_set = set(self.files)
        self._legacy = sorted(self.moves)
        self._dir_cache: dict[str, str | None] = {}

    # ---- the new world -------------------------------------------------------------------------
    def exists(self, ws_path: str) -> bool:
        p = ws_path.rstrip("/")
        if p in self._file_set:
            return True
        base = p + "/"
        i = bisect.bisect_left(self.files, base)
        return i < len(self.files) and self.files[i].startswith(base)

    # ---- the old world -------------------------------------------------------------------------
    def moved(self, legacy_path: str) -> str | None:
        """New workspace path of a legacy file or directory, or None when it did not move as a unit."""
        p = legacy_path.rstrip("/")
        if p in self.moves:
            return self.moves[p]
        if p in self._dir_cache:
            return self._dir_cache[p]
        base = p + "/"
        i = bisect.bisect_left(self._legacy, base)
        result: str | None = None
        ok = False
        while i < len(self._legacy) and self._legacy[i].startswith(base):
            old = self._legacy[i]
            new = self.moves[old]
            rest = old[len(base):]
            if not new.endswith("/" + rest) and new != rest:
                result, ok = None, False
                break
            cand = new[: len(new) - len(rest)].rstrip("/")
            if not ok and result is None:
                result, ok = cand, True
            elif cand != result:
                result, ok = None, False
                break
            i += 1
        out = result if ok else None
        self._dir_cache[p] = out
        return out

    def to_json(self) -> dict:
        return {"files": self.files, "moves": dict(sorted(self.moves.items()))}

    @staticmethod
    def from_json(doc: dict) -> "PathIndex":
        return PathIndex(list(doc["files"]), dict(doc["moves"]))


def build(target_manifest: dict, report: dict) -> PathIndex:
    moves: dict[str, str] = {}
    for row in report["files"]:
        if row["origin"] == "source" and row["primary"]:
            moves[row["source"]] = row["workspacePath"]  # copies (primary=false) are extra placements
    return PathIndex(list(target_manifest["files"]), moves)


def load(path: Path) -> PathIndex:
    return PathIndex.from_json(json.loads(Path(path).read_text(encoding="utf-8")))
