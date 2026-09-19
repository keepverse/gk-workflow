"""Hash manifests and the lossy check.

A migration is lossless when every legacy file is accounted for in the moved workspace:

  * dropped on purpose (an ownership rule with target `drop`), or
  * present at its planned location with the exact bytes the staging run produced
    (`report.json` row `sha256`) - identical to the source when no transform applied;

and every file in the moved workspace is explained by a report row, a template, or a repo's
`preserve` globs. The source manifest is taken independently from git (not from report.json), so a
corrupted blob read or a report that drifted from its source is caught too.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from kvsplit.apply import long_path
from kvsplit.globmatch import compile_glob
from kvsplit.rules import Layout
from kvsplit.source import GitSource


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_manifest(repo: Path, rev: str) -> dict:
    src = GitSource(repo, rev)
    blobs = src.load_blobs()
    return {
        "kind": "source",
        "sourceSha": src.sha,
        "files": {p: sha256(b) for p, b in sorted(blobs.items())},
    }


def _tracked(repo_dir: Path) -> list[str]:
    p = subprocess.run(["git", "-c", "core.longpaths=true", "-C", str(repo_dir), "ls-files", "-z"], capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git ls-files failed in {repo_dir}: {p.stderr.decode(errors='replace')}")
    return sorted(x.decode("utf-8") for x in p.stdout.split(b"\0") if x)


def workspace_manifest(workspace: Path, layout: Layout) -> dict:
    """sha256 of every tracked file in every repo of the workspace, keyed by workspace path."""
    workspace = Path(workspace)
    files: dict[str, str] = {}
    for r in layout.repos:
        d = workspace if r.dir in (".", "") else workspace / r.dir
        if not (d / ".git").exists():
            raise RuntimeError(f"{d} is not a git repository")
        for rel in _tracked(d):
            ws = rel if r.dir in (".", "") else f"{r.dir}/{rel}"
            files[ws] = sha256(long_path(d / rel).read_bytes())
    return {"kind": "workspace", "files": dict(sorted(files.items()))}


@dataclass(frozen=True)
class Loss:
    kind: str    # missing | altered | source-drift | unexplained | unaccounted-source
    path: str
    detail: str

    def to_json(self) -> dict:
        return {"kind": self.kind, "path": self.path, "detail": self.detail}


def lossy_check(source: dict, report: dict, target: dict, layout: Layout) -> list[Loss]:
    out: list[Loss] = []
    if source["sourceSha"] != report["sourceSha"]:
        out.append(Loss("source-drift", "", f"manifest {source['sourceSha']} != report {report['sourceSha']}"))
    src_files: dict[str, str] = source["files"]
    tgt_files: dict[str, str] = target["files"]
    rows = report["files"]
    placed_sources: set[str] = set()
    explained: set[str] = set()
    for row in rows:
        ws = row["workspacePath"]
        explained.add(ws)
        if row["origin"] == "source":
            sp = row["source"]
            placed_sources.add(sp)
            if sp not in src_files:
                out.append(Loss("source-drift", sp, "report row names a file the source manifest does not have"))
            elif not row.get("transforms") and src_files[sp] != row["sha256"]:
                out.append(Loss("source-drift", sp, "untransformed row whose staged hash differs from the source"))
        if ws not in tgt_files:
            out.append(Loss("missing", ws, f"planned from {row.get('source', 'template')}"))
        elif tgt_files[ws] != row["sha256"]:
            out.append(Loss("altered", ws, "moved bytes differ from the staged bytes"))
    dropped = set(report.get("dropped", []))
    for sp in src_files:
        if sp not in placed_sources and sp not in dropped:
            out.append(Loss("unaccounted-source", sp, "legacy file neither placed nor dropped"))
    preserve = {r.dir: [compile_glob(g) for g in r.preserve] for r in layout.repos}
    for ws in tgt_files:
        if ws in explained:
            continue
        repo = next((r for r in layout.repos if r.dir not in (".", "") and ws.startswith(r.dir + "/")), None)
        d = repo.dir if repo else "."
        rel = ws[len(d) + 1:] if repo else ws
        if not any(g.match(rel) for g in preserve.get(d, [])):
            out.append(Loss("unexplained", ws, "file in the moved workspace that no report row, template or preserve rule explains"))
    return sorted(out, key=lambda l: (l.kind, l.path))


def dump(obj: dict, path: Path) -> None:
    Path(path).write_bytes((json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
