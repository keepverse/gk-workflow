"""Produce the staged workspace, report.json and residue.json from pinned inputs.

Layout of the staging directory:
  <out>/.kvsplit-staging      marker; the tool only ever clears a directory carrying it
  <out>/workspace/...         exactly the Keepverse layout: root repo files at the top,
                              each sub-repo under its `dir`
  <out>/report.json           every emitted file: source, blob, repo, path, transforms, sha256
  <out>/residue.json          everything the tool could not decide
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import shutil
from dataclasses import dataclass
from pathlib import Path

from kvsplit import __version__
from kvsplit.check import run_checks
from kvsplit.classify import Classification, classify
from kvsplit.globmatch import compile_glob
from kvsplit.graph import build as build_graph
from kvsplit.residue import Residue, dedupe_sorted
from kvsplit.rules import DROP, Rules, load_rules
from kvsplit.scan import scan
from kvsplit.source import GitSource
from kvsplit.transforms import OWNS, REGISTRY, Ctx

MARKER = ".kvsplit-staging"


class StageError(RuntimeError):
    pass


@dataclass
class StagedFile:
    repo: str
    path: str
    data: bytes
    source: str | None      # legacy path, None for templates
    blob: str | None
    transforms: tuple[str, ...]
    origin: str             # source | template


@dataclass
class StageResult:
    files: list[StagedFile]
    residue: list[Residue]
    report: dict
    cls: Classification


def _dumps(obj) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def compute(source: GitSource, rules: Rules) -> StageResult:
    entries = source.entries()
    cls, residue = classify(entries, rules.ownership, rules.layout)
    blobs = source.load_blobs()
    kept = {p: b for p, b in blobs.items() if (pl := cls.place(p)) is not None and pl.repo != DROP}
    _, gres = build_graph(kept, cls)
    residue += gres

    tcompiled = [(t, compile_glob(t.pattern)) for t in rules.transforms]
    oid = {e.path: e.oid for e in entries}
    files: list[StagedFile] = []
    transformed: set[str] = set()
    comment_owned: set[str] = set()
    for old in sorted(kept):
        pl = cls.place(old)
        assert pl is not None
        for repo in (pl.repo, *pl.copies):
            data = kept[old]
            applied: list[str] = []
            for t, rx in tcompiled:
                if rx.match(old):
                    ctx = Ctx(cls, old, repo, pl.path, t)
                    data, tres = REGISTRY[t.kind](ctx, data)
                    residue += tres
                    applied.append(t.id)
                    (transformed if OWNS[t.kind] == "file" else comment_owned).add(old)
            files.append(StagedFile(repo, pl.path, data, old, oid[old], tuple(applied), "source"))

    taken = {(f.repo, f.path) for f in files}
    for repo in sorted(rules.templates):
        for path in sorted(rules.templates[repo]):
            if (repo, path) in taken:
                residue.append(Residue("destination-collision", f"templates/{repo}/{path}", f"{repo}:{path}", None,
                                       "template collides with a migrated file", "rule"))
                continue
            files.append(StagedFile(repo, path, rules.templates[repo][path], None, None, (), "template"))

    residue += scan(kept, cls, rules.scan, transformed, comment_owned)
    files.sort(key=lambda f: (cls.workspace_path(f.repo, f.path)))
    residue += run_checks(files, cls, rules)
    residue = dedupe_sorted(residue)

    counts: dict[str, int] = {r: 0 for r in rules.layout.ids()}
    for f in files:
        if f.origin == "source" and f.repo == cls.place(f.source).repo:  # type: ignore[arg-type]
            counts[f.repo] += 1
    dropped = sum(1 for p in blobs if (pl := cls.place(p)) is not None and pl.repo == DROP)
    unplaced = sum(1 for e in entries if cls.place(e.path) is None)
    digest = hashlib.sha256()
    rows = []
    for f in files:
        h = hashlib.sha256(f.data).hexdigest()
        ws = cls.workspace_path(f.repo, f.path)
        digest.update(ws.encode() + b"\0" + h.encode() + b"\0")
        row = {"repo": f.repo, "path": f.path, "workspacePath": ws, "sha256": h, "origin": f.origin}
        if f.source is not None:
            row["source"] = f.source
            row["blob"] = f.blob
        if f.transforms:
            row["transforms"] = list(f.transforms)
        rows.append(row)
    report = {
        "tool": "kvsplit",
        "toolVersion": __version__,
        "sourceSha": source.sha,
        "rulesDigest": rules.digest,
        "outputDigest": digest.hexdigest(),
        "reconciliation": {
            "tracked": len(entries),
            "placedPerRepo": counts,
            "dropped": dropped,
            "unplaced": unplaced,
            "balanced": sum(counts.values()) + dropped + unplaced == len(entries),
        },
        "residueByKind": _by_kind(residue),
        "files": rows,
    }
    return StageResult(files, residue, report, cls)


def _by_kind(residue: list[Residue]) -> dict[str, int]:
    out: dict[str, int] = {}
    for r in residue:
        out[r.kind] = out.get(r.kind, 0) + 1
    return dict(sorted(out.items()))


def _prepare_out(out: Path) -> None:
    if out.exists():
        if not (out / MARKER).exists():
            if any(out.iterdir()):
                raise StageError(f"{out} is not empty and has no {MARKER} marker; refusing to clear it")
        else:
            shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / MARKER).write_bytes(b"kvsplit staging directory; cleared on every stage run\n")


def write(result: StageResult, out: Path) -> None:
    out = Path(out)
    _prepare_out(out)
    ws = out / "workspace"
    for f in result.files:
        dest = ws / result.cls.workspace_path(f.repo, f.path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(f.data)
    (out / "report.json").write_bytes(_dumps(result.report))
    (out / "residue.json").write_bytes(_dumps({
        "sourceSha": result.report["sourceSha"],
        "rulesDigest": result.report["rulesDigest"],
        "toolVersion": result.report["toolVersion"],
        "items": [r.to_json() for r in result.residue],
    }))


def stage(source_repo: Path, rev: str, rules_dir: Path, out: Path) -> StageResult:
    rules = load_rules(rules_dir, set(REGISTRY))
    result = compute(GitSource(source_repo, rev), rules)
    write(result, out)
    return result
