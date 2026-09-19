"""Re-index path references in documents after a move.

For every document in the moved workspace (rules/reindex.v1.json `docGlobs`), each path reference is
resolved against the new index:

  * resolves as-is                                   -> left alone
  * resolves once its legacy target is mapped through the move map -> rewritten
      markdown links stay relative to the document; bare citations become workspace-relative
  * pointed at a real legacy path that no longer maps as a unit, or maps to nothing -> **stale**

Stale references are the agents' reconcile queue; the tool never guesses a target. Same index and same
documents give the same rewrites (deterministic, idempotent: a second run rewrites nothing).
"""

from __future__ import annotations

import bisect
import json
import posixpath
import re
from dataclasses import dataclass, field
from pathlib import Path

from kvsplit.apply import long_path
from kvsplit.globmatch import compile_glob
from kvsplit.index import PathIndex
from kvsplit.rules import RulesError

_MD_LINK = re.compile(r"(\]\()([^)\s#]+)((?:#[^)\s]*)?\))")


@dataclass(frozen=True)
class ReindexConfig:
    doc_globs: tuple[str, ...]
    skip: tuple[str, ...]
    citation_roots: tuple[str, ...]


def load_config(path: Path) -> ReindexConfig:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schemaVersion") != 1:
        raise RulesError("reindex: unsupported schemaVersion")
    extra = set(doc) - {"schemaVersion", "docGlobs", "skip", "citationRoots"}
    if extra:
        raise RulesError(f"reindex: unknown field(s) {sorted(extra)}")
    for k in ("docGlobs", "skip", "citationRoots"):
        if not isinstance(doc.get(k), list):
            raise RulesError(f"reindex: '{k}' must be a list")
    for g in (*doc["docGlobs"], *doc["skip"]):
        compile_glob(g)
    return ReindexConfig(tuple(doc["docGlobs"]), tuple(doc["skip"]), tuple(doc["citationRoots"]))


@dataclass
class Finding:
    doc: str
    line: int
    ref: str
    new: str | None
    reason: str

    def to_json(self) -> dict:
        d = {"doc": self.doc, "line": self.line, "ref": self.ref, "reason": self.reason}
        if self.new is not None:
            d["new"] = self.new
        return d


@dataclass
class Result:
    rewritten: list[Finding] = field(default_factory=list)
    stale: list[Finding] = field(default_factory=list)
    pre_existing: list[Finding] = field(default_factory=list)  # broken before the move; not the move's to fix
    changed: dict[str, bytes] = field(default_factory=dict)  # workspace path -> new bytes


def _legacy_exists(index: PathIndex, legacy: str) -> bool:
    p = legacy.rstrip("/")
    if p in index.moves:
        return True
    keys = index._legacy
    i = bisect.bisect_left(keys, p + "/")
    return i < len(keys) and keys[i].startswith(p + "/")


def _cite_regex(roots: tuple[str, ...]) -> re.Pattern[str]:
    alt = "|".join(re.escape(r) for r in roots)
    return re.compile(r"(?<![\w./\-])((?:" + alt + r")/[\w.\-/]*[\w\-])((?::\d+(?:-\d+)?)?)")


def reindex_text(doc_ws: str, text: str, index: PathIndex, reverse: dict[str, str],
                 cfg: ReindexConfig, result: Result) -> str:
    legacy_doc = reverse.get(doc_ws)
    doc_dir = posixpath.dirname(doc_ws) or "."
    first = doc_ws.split("/", 1)[0]
    repo_prefix = first + "/" if first.startswith("gk-") and "/" in doc_ws else ""

    def line_of(pos: int) -> int:
        return text.count("\n", 0, pos) + 1

    def link(m: re.Match[str]) -> str:
        target = m.group(2)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("/"):
            return m.group(0)
        if "/" not in target and "." not in target:
            return m.group(0)  # a bare slug is an in-app route (guide page id), not a file path
        now = posixpath.normpath(posixpath.join(doc_dir, target))
        if not now.startswith("..") and index.exists(now):
            return m.group(0)
        if legacy_doc is None:
            result.stale.append(Finding(doc_ws, line_of(m.start()), target, None, "unresolved link in a document with no legacy origin"))
            return m.group(0)
        legacy_target = posixpath.normpath(posixpath.join(posixpath.dirname(legacy_doc), target))
        new = None if legacy_target.startswith("..") else index.moved(legacy_target)
        if new is None or not index.exists(new):
            if _legacy_exists(index, legacy_target):
                result.stale.append(Finding(doc_ws, line_of(m.start()), target, None,
                                            "legacy target split across repos or dropped"))
            else:
                result.pre_existing.append(Finding(doc_ws, line_of(m.start()), target, None,
                                                   "already broken before the move"))
            return m.group(0)
        rel = posixpath.relpath(new, doc_dir)
        if target.endswith("/") and not rel.endswith("/"):
            rel += "/"
        result.rewritten.append(Finding(doc_ws, line_of(m.start()), target, rel, "link"))
        return m.group(1) + rel + m.group(3)

    text = _MD_LINK.sub(link, text)
    if cfg.citation_roots:
        rx = _cite_regex(cfg.citation_roots)

        def cite(m: re.Match[str]) -> str:
            ref = m.group(1)
            if index.exists(ref) or (repo_prefix and index.exists(repo_prefix + ref)):
                return m.group(0)  # resolves workspace-relative, or relative to the document's own repo
            new = index.moved(ref)
            if new is not None and index.exists(new):
                result.rewritten.append(Finding(doc_ws, line_of(m.start()), ref, new, "citation"))
                return new + m.group(2)
            if _legacy_exists(index, ref):
                result.stale.append(Finding(doc_ws, line_of(m.start()), ref, None, "legacy path split across repos or dropped"))
            return m.group(0)  # never existed: prose, a placeholder, or a future file

        text = rx.sub(cite, text)
    return text


def reindex(workspace: Path, index: PathIndex, cfg: ReindexConfig) -> Result:
    workspace = Path(workspace)
    docs = [compile_glob(g) for g in cfg.doc_globs]
    skip = [compile_glob(g) for g in cfg.skip]
    reverse = {v: k for k, v in index.moves.items()}
    result = Result()
    for ws in index.files:
        if not any(g.match(ws) for g in docs) or any(s.match(ws) for s in skip):
            continue
        raw = long_path(workspace / ws).read_bytes()
        bom = raw.startswith(b"\xef\xbb\xbf")
        try:
            text = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
        except UnicodeDecodeError:
            result.stale.append(Finding(ws, 0, "", None, "document is not UTF-8; not re-indexed"))
            continue
        new = reindex_text(ws, text, index, reverse, cfg, result)
        if new != text:
            result.changed[ws] = (b"\xef\xbb\xbf" if bom else b"") + new.encode("utf-8")
    result.rewritten.sort(key=lambda f: (f.doc, f.line, f.ref))
    result.stale.sort(key=lambda f: (f.doc, f.line, f.ref))
    result.pre_existing.sort(key=lambda f: (f.doc, f.line, f.ref))
    return result


def write(result: Result, workspace: Path, apply: bool, report_path: Path) -> None:
    if apply:
        for ws, data in sorted(result.changed.items()):
            long_path(Path(workspace) / ws).write_bytes(data)
    doc = {
        "applied": apply,
        "changedDocuments": sorted(result.changed),
        "rewritten": [f.to_json() for f in result.rewritten],
        "stale": [f.to_json() for f in result.stale],
        "preExisting": [f.to_json() for f in result.pre_existing],
    }
    Path(report_path).write_bytes((json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
