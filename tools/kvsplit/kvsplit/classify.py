"""Assign every tracked path to exactly one target repo, and map old paths to new locations.

Resolution: among the rules whose pattern matches a path, the highest `priority` wins. Two
winners at the same priority is ambiguous -> residue. No match -> residue. A rule that matches
nothing -> residue (a dead rule is a wrong rule).
"""

from __future__ import annotations

import bisect
import posixpath
from dataclasses import dataclass

from kvsplit.globmatch import compile_glob
from kvsplit.residue import Residue
from kvsplit.rules import DROP, Layout, OwnershipRule
from kvsplit.source import Entry


@dataclass(frozen=True)
class Placement:
    repo: str        # target repo id, or DROP
    path: str        # new path inside that repo
    rule: str        # winning rule id
    copies: tuple[str, ...]


class Classification:
    def __init__(self, layout: Layout, placements: dict[str, Placement]) -> None:
        self.layout = layout
        self.placements = placements
        self._dir_cache: dict[str, tuple[str, str] | None] = {}
        self._sorted = sorted(placements)

    def place(self, path: str) -> Placement | None:
        return self.placements.get(path)

    def map_file(self, path: str) -> tuple[str, str] | None:
        p = self.placements.get(path)
        if p is None or p.repo == DROP:
            return None
        return p.repo, p.path

    def map_dir(self, prefix: str) -> tuple[str, str] | None:
        """Map a directory prefix. Every kept file under it must land in one repo at one offset."""
        prefix = prefix.rstrip("/")
        if prefix in self._dir_cache:
            return self._dir_cache[prefix]
        result: tuple[str, str] | None = None
        consistent = True
        found = False
        base = prefix + "/" if prefix else ""
        i = bisect.bisect_left(self._sorted, base)
        while i < len(self._sorted) and self._sorted[i].startswith(base):
            old = self._sorted[i]
            i += 1
            p = self.placements[old]
            if p.repo == DROP:
                continue
            rest = old[len(base):]
            if not p.path.endswith(rest):
                consistent = False
                break
            new_prefix = p.path[: len(p.path) - len(rest)].rstrip("/")
            cand = (p.repo, new_prefix)
            if not found:
                result, found = cand, True
            elif cand != result:
                consistent = False
                break
        out = result if (found and consistent) else None
        self._dir_cache[prefix] = out
        return out

    def map_any(self, path: str) -> tuple[str, str] | None:
        path = path.rstrip("/")
        return self.map_file(path) or self.map_dir(path)

    def workspace_path(self, repo: str, path: str) -> str:
        d = self.layout.repo(repo).dir
        return path if d in (".", "") else posixpath.join(d, path) if path else d


def classify(entries: list[Entry], rules: tuple[OwnershipRule, ...], layout: Layout) -> tuple[Classification, list[Residue]]:
    residue: list[Residue] = []
    compiled = [(r, compile_glob(r.pattern)) for r in rules]
    hits: dict[str, int] = {r.id: 0 for r in rules}
    placements: dict[str, Placement] = {}
    for e in entries:
        if e.kind != "blob" or e.mode == "120000":
            # A rule targeting `drop` is an explicit statement that this path must not
            # exist in the output, so it authorises dropping a non-blob entry too. That
            # is the only way to retire a symlink: a symlink cannot be migrated (git
            # checks it out as plain text without core.symlinks), and it never reaches
            # ordinary classification, so without this it would be unresolvable residue.
            droppers = [r for r, rx in compiled if r.target == DROP and rx.match(e.path)]
            if droppers:
                top = max(r.priority for r in droppers)
                winner = next(r for r in droppers if r.priority == top)
                for r in droppers:
                    hits[r.id] += 1
                # Record the placement so the reconciliation counts this path as dropped
                # rather than unplaced: a `dropped` total that excludes retired symlinks
                # is a smaller number than the work actually done.
                placements[e.path] = Placement(DROP, e.path, winner.id, ())
                continue
            residue.append(Residue("unsupported-entry", e.path, e.mode, None,
                                   f"git entry kind={e.kind} mode={e.mode} (submodule/symlink) is not migrated automatically",
                                   "rule"))
            continue
        matched = [r for r, rx in compiled if rx.match(e.path)]
        for r in matched:
            hits[r.id] += 1
        if not matched:
            residue.append(Residue("unowned-path", e.path, "", None, "no ownership rule matches this path", "rule"))
            continue
        top = max(r.priority for r in matched)
        winners = [r for r in matched if r.priority == top]
        if len(winners) > 1:
            ids = ",".join(sorted(w.id for w in winners))
            residue.append(Residue("ambiguous-path", e.path, ids, None,
                                   f"rules {ids} match at the same priority {top}", "rule"))
            continue
        w = winners[0]
        new = e.path
        if w.relocate is not None:
            if not e.path.startswith(w.relocate.src):
                residue.append(Residue("bad-relocation", e.path, w.id, None,
                                       f"rule {w.id} relocates from '{w.relocate.src}' but the path does not start with it",
                                       "rule"))
                continue
            new = w.relocate.dst + e.path[len(w.relocate.src):]
        placements[e.path] = Placement(w.target, new, w.id, w.copies)
    for r in rules:
        if hits[r.id] == 0:
            residue.append(Residue("dead-rule", "rules/ownership.v1.json", r.id, None,
                                   f"rule {r.id} ({r.pattern}) matches no tracked path", "rule"))
    # two sources landing on one destination is a collision
    dest: dict[tuple[str, str], str] = {}
    for old in sorted(placements):
        p = placements[old]
        if p.repo == DROP:
            continue
        for repo in (p.repo, *p.copies):
            key = (repo, p.path)
            if key in dest:
                residue.append(Residue("destination-collision", old, f"{repo}:{p.path}", None,
                                       f"also produced by {dest[key]}", "rule"))
            else:
                dest[key] = old
    return Classification(layout, placements), residue
