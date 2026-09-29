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


def _git(repo_dir: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-c", "core.longpaths=true", "-C", str(repo_dir), *args],
                          capture_output=True)


def _import_ref(repo_dir: Path) -> str | None:
    """The commit kvsplit wrote into this repo, if apply has run there."""
    p = _git(repo_dir, "log", "--format=%H", "-1", "--grep=^Import snapshot from legacy repo")
    out = p.stdout.decode("utf-8", "replace").strip()
    return out or None


def _paths_at(repo_dir: Path, ref: str) -> set[str] | None:
    p = _git(repo_dir, "ls-tree", "-r", "--name-only", "-z", ref)
    if p.returncode != 0:
        return None
    return {x.decode("utf-8", "replace") for x in p.stdout.split(b"\0") if x}


def workspace_manifest(workspace: Path, layout: Layout) -> dict:
    """sha256 of every tracked file in every repo of the workspace, keyed by workspace path.

    Also records each repo's import commit, so the lossy check can tell a file the
    migration invented apart from work committed after the import. Without that
    distinction every later commit reads as an unexplained file and the gate can never
    pass on a workspace anyone has done anything to.
    """
    workspace = Path(workspace)
    files: dict[str, str] = {}
    import_refs: dict[str, str] = {}
    post_import: dict[str, list[str]] = {}
    for r in layout.repos:
        d = workspace if r.dir in (".", "") else workspace / r.dir
        if not (d / ".git").exists():
            raise RuntimeError(f"{d} is not a git repository")
        tracked = _tracked(d)
        for rel in tracked:
            ws = rel if r.dir in (".", "") else f"{r.dir}/{rel}"
            files[ws] = sha256(long_path(d / rel).read_bytes())
        ref = _import_ref(d)
        if ref:
            import_refs[r.dir] = ref
            before = _paths_at(d, ref)
            if before is not None:
                after = {
                    "created": sorted(x for x in tracked if x not in before),
                    "deleted": sorted(before - set(tracked)),
                }
                post_import[r.dir] = [f"{k}:{v}" for k, vs in after.items() for v in vs]
    return {"kind": "workspace", "files": dict(sorted(files.items())),
            "importRefs": import_refs, "postImport": post_import}


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

    # A repo the split places no PRIMARY source content into is out of scope, and apply
    # leaves it byte-identical. gk-assets is out of scope by owner decision and gk-tests by
    # design. Their files are therefore not unexplained, and the report's rows for them are
    # never written - so they are not missing or altered either. Deriving this the same way
    # apply does is the point: two places computing "in scope" differently is how 209 art
    # files got deleted.
    in_scope = {r["repo"] for r in rows if r.get("origin") == "source" and r.get("primary")}

    preserve = {r.dir: [compile_glob(g) for g in r.preserve] for r in layout.repos}

    def preserved(ws: str) -> bool:
        repo = next((r for r in layout.repos if r.dir not in (".", "") and ws.startswith(r.dir + "/")), None)
        d = repo.dir if repo else "."
        rel = ws[len(d) + 1:] if repo else ws
        return any(g.match(rel) for g in preserve.get(d, []))

    placed_sources: set[str] = set()
    explained: set[str] = set()
    for row in rows:
        ws = row["workspacePath"]
        rid = row["repo"]
        if rid in in_scope:
            explained.add(ws)
        if row["origin"] == "source":
            sp = row["source"]
            placed_sources.add(sp)
            if sp not in src_files:
                out.append(Loss("source-drift", sp, "report row names a file the source manifest does not have"))
            elif not row.get("transforms") and src_files[sp] != row["sha256"]:
                out.append(Loss("source-drift", sp, "untransformed row whose staged hash differs from the source"))
        if rid not in in_scope:
            continue                      # out of scope: nothing was planned to be written
        if ws not in tgt_files:
            out.append(Loss("missing", ws, f"planned from {row.get('source', 'template')}"))
        elif tgt_files[ws] != row["sha256"] and not preserved(ws):
            # `preserve` means the repository's copy is authoritative, so different bytes are
            # the design working, not drift. Reporting it as `altered` made a deliberate
            # 234-line .gitignore look like data loss.
            out.append(Loss("altered", ws, "moved bytes differ from the staged bytes"))
    dropped = set(report.get("dropped", []))
    for sp in src_files:
        if sp not in placed_sources and sp not in dropped:
            out.append(Loss("unaccounted-source", sp, "legacy file neither placed nor dropped"))

    # Work committed after the import commit is not the migration's to explain. It is
    # reported under its own kind so it stays visible and countable, and never counted as a
    # migration defect - otherwise every later commit reads as an unexplained file and the
    # gate can never pass on a workspace anyone has done anything to.
    post = {f"{d}/{p.split(':', 1)[1]}" if d != "." else p.split(":", 1)[1]
            for d, entries in target.get("postImport", {}).items()
            for p in entries if p.startswith("created:")}
    subrepos = sorted((r for r in layout.repos if r.dir not in (".", "")), key=lambda r: -len(r.dir))
    by_id = {r.id: r for r in layout.repos}

    def repo_id_of(ws: str) -> str:
        for r in subrepos:
            if ws.startswith(r.dir + "/"):
                return r.id
        return by_id["root"].id

    for ws in tgt_files:
        if ws in explained or preserved(ws):
            continue
        if ws in post:
            out.append(Loss("post-import", ws, "committed after the import; not the migration's to explain"))
            continue
        if repo_id_of(ws) not in in_scope:
            continue                      # out of scope: the repo is left byte-identical
        out.append(Loss("unexplained", ws, "file in the moved workspace that no report row, template or preserve rule explains"))
    return sorted(out, key=lambda l: (l.kind, l.path))


def dump(obj: dict, path: Path) -> None:
    Path(path).write_bytes((json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
