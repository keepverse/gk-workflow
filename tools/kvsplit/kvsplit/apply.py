"""Commit a staged repo into its Keepverse repository as one snapshot commit.

The only verb that writes outside the staging directory. It refuses unless:
  * the caller passes the explicit migration-start confirmation (owner gate GM);
  * residue.json is empty, unless the move-first flow carries it (allow_residue) into the
    post-move lossy check, reindex and agent reconcile;
  * the target repo is a git repo with a clean status;
  * for the root repo, the staged .gitignore excludes every sub-repo directory.
Tracked files not matched by the repo's `preserve` globs are replaced by the staged tree.
It commits locally only; it never pushes.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

from kvsplit.globmatch import compile_glob
from kvsplit.rules import Layout


class ApplyError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    # core.longpaths: moved trees nest deeper than the legacy repo; Windows MAX_PATH must not decide the move.
    p = subprocess.run(["git", "-c", "core.longpaths=true", "-C", str(repo), *args],
                       capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise ApplyError(f"git {' '.join(args)} in {repo}: {p.stderr.strip()}")
    return p.stdout


def _git_in(repo: Path, stdin: str, *args: str) -> str:
    p = subprocess.run(["git", "-c", "core.longpaths=true", "-C", str(repo), *args],
                       input=stdin.encode("utf-8"), capture_output=True)
    if p.returncode != 0:
        raise ApplyError(f"git {' '.join(args)} in {repo}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode("utf-8")


def long_path(p: Path) -> Path:
    """An absolute path usable past MAX_PATH on Windows (extended-length prefix); unchanged elsewhere."""
    if os.name != "nt":
        return p
    s = str(Path(p).resolve())
    return Path(s if s.startswith("\\\\?\\") else "\\\\?\\" + s)


def _target(workspace: Path, layout: Layout, rid: str) -> Path:
    repo = layout.repo(rid)
    return workspace if repo.dir in (".", "") else workspace / repo.dir


def _digest(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _overwrites(staging: Path, workspace: Path, layout: Layout, repo_ids: list[str],
                report: dict) -> list[str]:
    """Staged paths that already exist in a target repo with different content.

    A path the repo preserves is kept rather than written, so it can never be an
    overwrite and is not listed. Everything else: without this an owner who already
    migrated and then improved a file loses the improvement with no warning, and a
    .blend scene or a rendered sheet is not something a text diff would make obvious
    afterwards. The staged `.gitignore` is the case that must land here - the live ones
    are generic templates without `**/dist/`, `**/node_modules/` or the runtime
    databases, so overwriting the template with it is a correction, not a loss.
    """
    out: list[str] = []
    for rid in repo_ids:
        keep = [compile_glob(g) for g in layout.repo(rid).preserve]
        for r in report["files"]:
            if r["repo"] != rid or any(k.match(r["path"]) for k in keep):
                continue
            live = _target(workspace, layout, rid) / r["path"]
            src = long_path(staging / "workspace" / r["workspacePath"])
            if not live.is_file() or not src.is_file():
                continue
            if _digest(live) != _digest(src):
                out.append(f"{rid}/{r['path']}")
    return out


def _unmigrated(repo_ids: list[str], report: dict) -> set[str]:
    """Repos the split places zero files into: gk-assets, and gk-tests by design.

    These are not part of the migration, so preflight must not validate them as if they
    were. The delete loop runs regardless of what a repo receives, so a repo in this set
    that went through it would lose every unpreserved tracked file - for gk-assets that was
    209 of 228, the whole art tree. Decided once, here, so preflight and the write loop
    cannot disagree about whether such a repo is in scope.
    """
    counts: dict[str, int] = {}
    for r in report["files"]:
        counts[r["repo"]] = counts.get(r["repo"], 0) + 1
    return {rid for rid in repo_ids if not counts.get(rid)}


def _preflight(staging: Path, workspace: Path, layout: Layout, repo_ids: list[str],
               report: dict, accept_overwrites: bool = False) -> set[str]:
    """Every check for every repo, before a single byte is written: no half-applied workspace.

    Returns the repos that are out of scope, so the caller writes nothing to them.
    """
    unmigrated = _unmigrated(repo_ids, report)
    in_scope = [rid for rid in repo_ids if rid not in unmigrated]
    sub_dirs = [r.dir for r in layout.repos if r.dir not in (".", "")]
    for rid in in_scope:
        repo = layout.repo(rid)
        target = _target(workspace, layout, rid)
        if not (target / ".git").exists():
            raise ApplyError(f"{target} is not a git repository")
        status = [ln for ln in _git(target, "status", "--porcelain").splitlines() if ln.strip()]
        if repo.dir in (".", ""):
            status = [ln for ln in status if not any(ln[3:].rstrip("/") == d for d in sub_dirs)]
            gi = staging / "workspace" / ".gitignore"
            lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
            missing = [d for d in sub_dirs if f"/{d}/" not in lines and f"{d}/" not in lines]
            if missing:
                raise ApplyError(f"staged root .gitignore must exclude sub-repo dirs {missing}")
        if status:
            raise ApplyError(f"{target} is not clean:\n" + "\n".join(status))
    for r in report["files"]:
        if r["repo"] in in_scope and not long_path(staging / "workspace" / r["workspacePath"]).is_file():
            raise ApplyError(f"staged file missing: {r['workspacePath']}; re-run stage")
    if not accept_overwrites:
        clashes = _overwrites(staging, workspace, layout, in_scope, report)
        if clashes:
            shown = "\n".join(f"  {c}" for c in clashes[:20])
            more = f"\n  ... and {len(clashes) - 20} more" if len(clashes) > 20 else ""
            raise ApplyError(
                f"apply would overwrite {len(clashes)} existing file(s) with different "
                f"content. These are already-committed files in the target repos, so this "
                f"is silent data loss, not a fresh write.\n{shown}{more}\n"
                f"Reconcile them (move the newer file, or drop it from preserve and let the "
                f"split own the path), or pass --accept-overwrites to overwrite deliberately."
            )
    return unmigrated


def apply(staging: Path, workspace: Path, layout: Layout, repo_ids: list[str], rules_digest: str,
          confirm_migration_start: bool, allow_residue: bool = False,
          accept_overwrites: bool = False) -> list[str]:
    if not confirm_migration_start:
        raise ApplyError("apply is held behind gate GM: pass --confirm-migration-start only on the owner's command")
    staging, workspace = Path(staging), Path(workspace)
    residue = json.loads((staging / "residue.json").read_text(encoding="utf-8"))
    if residue["items"] and not allow_residue:
        raise ApplyError(f"residue is not empty ({len(residue['items'])} items); reconcile first")
    report = json.loads((staging / "report.json").read_text(encoding="utf-8"))
    if report["rulesDigest"] != rules_digest:
        raise ApplyError("staging was produced by different rules; re-run stage")
    unmigrated = _preflight(staging, workspace, layout, repo_ids, report, accept_overwrites)
    commits = []
    for rid in repo_ids:
        repo = layout.repo(rid)
        target = _target(workspace, layout, rid)
        # Out of scope, decided in preflight: no delete loop, no write, no commit. A repo
        # the split places nothing into is not part of the migration, and the delete loop
        # runs regardless of what a repo receives - so letting one through would strip
        # every unpreserved file for no reason.
        if rid in unmigrated:
            commits.append(f"{rid}: untouched (the split places no files here)")
            continue
        keep = [compile_glob(g) for g in repo.preserve]
        for tracked in _git(target, "ls-files", "-z").split("\0"):
            if tracked and not any(k.match(tracked) for k in keep):
                long_path(target / tracked).unlink()
        kept: list[str] = []
        for r in (r for r in report["files"] if r["repo"] == rid):
            # `preserve` means this path is the repo's, not the split's. It already stops
            # apply deleting the file; it must also stop apply writing over it, or a
            # hand-authored AGENTS.md is silently replaced by the weaker template that
            # exists only to seed a repo that lacks one. Reported, never silent.
            if any(k.match(r["path"]) for k in keep):
                kept.append(r["path"])
                continue
            dest = long_path(target / r["path"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(long_path(staging / "workspace" / r["workspacePath"]).read_bytes())
        _git(target, "add", "-A", "--", ".")  # records deletions
        # force-add every planned file: a copied .gitignore must never silently drop a tracked legacy file
        planned = [r["path"] for r in report["files"]
                   if r["repo"] == rid and not any(k.match(r["path"]) for k in keep)]
        if planned:  # pathspec on stdin: no command-line length limit, no quoting
            _git_in(target, "\0".join(planned) + "\0", "add", "-f", "--pathspec-from-file=-", "--pathspec-file-nul")
        # A repo that receives nothing and loses nothing has no commit to make, and
        # `git commit` on an empty index is an error. That is a legitimate state - a repo
        # that holds hand-authored gate definitions is meant to receive zero migrated
        # files - so it is reported, not treated as a failure.
        pending = [ln for ln in _git(target, "status", "--porcelain").splitlines() if ln.strip()]
        note = ("  [kept " + str(len(kept)) + " preserved: " + ", ".join(sorted(kept))
                + (", ..." if len(kept) > 3 else "") + "]") if kept else ""
        if not pending:
            commits.append(f"{rid}: unchanged (nothing staged for this repo){note}")
            continue
        msg = (f"Import snapshot from legacy repo {report['sourceSha']}\n\n"
               f"Produced by kvsplit {report['toolVersion']}, rules digest {report['rulesDigest']},\n"
               f"output digest {report['outputDigest']}. Do not edit by hand: change the rules and re-run.\n")
        _git(target, "commit", "-q", "-m", msg)
        commits.append(f"{rid}: {_git(target, 'rev-parse', 'HEAD').strip()}{note}")
    return commits
