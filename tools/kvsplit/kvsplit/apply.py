"""Commit a staged repo into its Keepverse repository as one snapshot commit.

The only verb that writes outside the staging directory. It refuses unless:
  * the caller passes the explicit migration-start confirmation (owner gate GM);
  * residue.json is empty;
  * the target repo is a git repo with a clean status;
  * for the root repo, the staged .gitignore excludes every sub-repo directory.
Tracked files not matched by the repo's `preserve` globs are replaced by the staged tree.
It commits locally only; it never pushes.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from kvsplit.globmatch import compile_glob
from kvsplit.rules import Layout


class ApplyError(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        raise ApplyError(f"git {' '.join(args)} in {repo}: {p.stderr.strip()}")
    return p.stdout


def apply(staging: Path, workspace: Path, layout: Layout, repo_ids: list[str], rules_digest: str,
          confirm_migration_start: bool) -> list[str]:
    if not confirm_migration_start:
        raise ApplyError("apply is held behind gate GM: pass --confirm-migration-start only on the owner's command")
    staging, workspace = Path(staging), Path(workspace)
    residue = json.loads((staging / "residue.json").read_text(encoding="utf-8"))
    if residue["items"]:
        raise ApplyError(f"residue is not empty ({len(residue['items'])} items); reconcile first")
    report = json.loads((staging / "report.json").read_text(encoding="utf-8"))
    if report["rulesDigest"] != rules_digest:
        raise ApplyError("staging was produced by different rules; re-run stage")
    commits = []
    for rid in repo_ids:
        repo = layout.repo(rid)
        target = workspace if repo.dir in (".", "") else workspace / repo.dir
        if not (target / ".git").exists():
            raise ApplyError(f"{target} is not a git repository")
        sub_dirs = [r.dir for r in layout.repos if r.dir not in (".", "")]
        status = [ln for ln in _git(target, "status", "--porcelain").splitlines() if ln.strip()]
        if rid == "root" or repo.dir in (".", ""):
            status = [ln for ln in status if not any(ln[3:].rstrip("/") == d for d in sub_dirs)]
            gi = staging / "workspace" / ".gitignore"
            lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
            missing = [d for d in sub_dirs if f"/{d}/" not in lines and f"{d}/" not in lines]
            if missing:
                raise ApplyError(f"staged root .gitignore must exclude sub-repo dirs {missing}")
        if status:
            raise ApplyError(f"{target} is not clean:\n" + "\n".join(status))
        keep = [compile_glob(g) for g in repo.preserve]
        for tracked in _git(target, "ls-files", "-z").split("\0"):
            if tracked and not any(k.match(tracked) for k in keep):
                (target / tracked).unlink()
        rows = [r for r in report["files"] if r["repo"] == rid]
        for r in rows:
            src = staging / "workspace" / r["workspacePath"]
            dest = target / r["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(src.read_bytes())
        _git(target, "add", "-A", "--", ".")
        msg = (f"Import snapshot from legacy repo {report['sourceSha']}\n\n"
               f"Produced by kvsplit {report['toolVersion']}, rules digest {report['rulesDigest']},\n"
               f"output digest {report['outputDigest']}. Do not edit by hand: change the rules and re-run.\n")
        _git(target, "commit", "-q", "-m", msg)
        commits.append(f"{rid}: {_git(target, 'rev-parse', 'HEAD').strip()}")
    return commits
