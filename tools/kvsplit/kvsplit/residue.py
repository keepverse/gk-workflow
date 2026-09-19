"""Residue: everything the deterministic pass could not decide. The agents' work queue.

Each item's `id` is stable across runs (hash of kind + path + anchor), so an agent can prove an
item is closed: a re-run no longer emits that id and emits no new one.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Residue:
    kind: str
    path: str
    anchor: str          # what inside the path: a token, a rule id, an attribute value
    line: int | None
    detail: str
    allowed_fix: str     # rule | transform | source

    @property
    def id(self) -> str:
        return hashlib.sha256(f"{self.kind}\0{self.path}\0{self.anchor}".encode()).hexdigest()[:16]

    def to_json(self) -> dict:
        d = {
            "id": self.id,
            "kind": self.kind,
            "path": self.path,
            "anchor": self.anchor,
            "detail": self.detail,
            "allowedFix": self.allowed_fix,
        }
        if self.line is not None:
            d["line"] = self.line
        return d


def dedupe_sorted(items: list[Residue]) -> list[Residue]:
    seen: dict[str, Residue] = {}
    for r in sorted(items, key=lambda r: (r.kind, r.path, r.line or 0, r.anchor)):
        seen.setdefault(r.id, r)
    return sorted(seen.values(), key=lambda r: (r.kind, r.path, r.line or 0, r.anchor))
