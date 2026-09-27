#!/usr/bin/env python3
"""Recreate the per-tool skill aliases from the canonical .agents/skills tree.

The legacy repo carried two sets of tracked symlinks -- `.claude/skills/<name>` and
`.kiro/skills/<name>` -- both pointing at `../../.agents/skills/<name>`. kvsplit drops
them, because a symlink in git is a filesystem artifact: with the default
`core.symlinks=false` a Windows checkout writes the link *target* as a plain text file
and the skill silently stops existing. Two alias sets of the same 111 skills would also
drift apart on their own.

So the canonical content is the only thing that is tracked, and this script rebuilds the
aliases. Run it once after cloning or migrating the workspace:

    python tools/bootstrap_skills.py

Idempotent, and it never overwrites a real directory with a link.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

CANONICAL = ".agents/skills"
# tool config dir -> the subdirectory inside that dir the tool reads skills from
ALIAS_ROOTS = (".claude/skills", ".kiro/skills")
# A directory is the workspace root only if it holds the canonical tree AND one of
# these. Without the second condition the upward walk finds a developer's home
# directory, which on a machine with a global skill install looks exactly like a
# workspace - and then this script writes links into it.
WORKSPACE_MARKERS = ("Keepverse.code-workspace", "tools/kvsplit", "AGENTS.md")


def is_workspace_root(d: Path) -> bool:
    """True only for a real workspace root: the skills tree plus a root-only marker."""
    if not (d / CANONICAL).is_dir():
        return False
    return any((d / m).exists() for m in WORKSPACE_MARKERS)


def find_root(start: Path) -> Path:
    """Nearest ancestor that is genuinely the workspace root, or a refusal.

    Never guesses: a wrong root here means writing symlinks into an unrelated tree.
    """
    for cand in (start, *start.parents):
        if is_workspace_root(cand):
            return cand
    raise SystemExit(
        f"refusing to run: no workspace root at or above {start}.\n"
        f"A workspace root holds {CANONICAL}/ plus one of {', '.join(WORKSPACE_MARKERS)}.\n"
        "Pass --root explicitly if this tree is not the Keepverse workspace."
    )


def is_link_or_missing(path: Path) -> bool:
    """True when `path` is safe to replace: absent, or already a symlink."""
    if path.is_symlink():
        return True
    return not path.exists()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=None,
                    help="workspace root; defaults to the nearest ancestor holding " + CANONICAL)
    ap.add_argument("--check", action="store_true",
                    help="report what is missing without writing anything")
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    ap.add_argument("--timeout", type=float, default=30.0,
                    help="hard ceiling on the whole run, in seconds")
    args = ap.parse_args(argv)

    started = time.monotonic()

    def out_of_time() -> bool:
        return time.monotonic() - started > args.timeout

    refusal: str | None = None
    root: Path | None = None
    if args.root is not None:
        # An explicit --root is used exactly as given. Walking up from it would let a
        # typo silently operate on a parent tree.
        root = args.root.resolve()
        if not is_workspace_root(root):
            refusal = (f"--root {root} is not a workspace root: it must hold "
                       f"{CANONICAL}/ plus one of {', '.join(WORKSPACE_MARKERS)}")
    else:
        try:
            root = find_root(Path.cwd().resolve())
        except SystemExit as ex:
            refusal = str(ex)

    if refusal is not None or root is None:
        print(json.dumps({"ok": False, "refusal": refusal,
                          "candidates": list(WORKSPACE_MARKERS)}))
        return 2

    src_root = root / CANONICAL
    if not src_root.is_dir():
        print(json.dumps({"ok": False, "refusal": f"{src_root} is not a directory"}))
        return 2

    created: list[str] = []
    repaired: list[str] = []
    skipped: list[str] = []
    missing: list[str] = []
    pruned: list[str] = []
    would_create: list[str] = []
    would_repair: list[str] = []
    would_prune: list[str] = []

    for alias_root in ALIAS_ROOTS:
        base = root / alias_root
        if out_of_time():
            break
        if not args.check:
            base.mkdir(parents=True, exist_ok=True)
        for skill in sorted(src_root.iterdir()):
            if not skill.is_dir():
                continue
            if out_of_time():
                break
            alias = base / skill.name
            rel = os.path.relpath(skill, alias.parent)
            if alias.is_symlink():
                # Correct only if the relative form is right AND the target is there. A
                # link with the right text but a missing target is dangling, and the
                # canonical tree is the source of truth, so it gets rebuilt.
                if Path(os.readlink(alias)) == Path(rel) and alias.exists():
                    skipped.append(str(alias.relative_to(root)))
                else:
                    if args.check:
                        would_repair.append(str(alias.relative_to(root)))
                        continue
                    alias.unlink()
                    alias.symlink_to(rel, target_is_directory=True)
                    repaired.append(str(alias.relative_to(root)))
                continue
            if alias.exists():
                # A real directory here is a real skill, not a stale alias. Never clobber it.
                skipped.append(str(alias.relative_to(root)))
                continue
            if args.check:
                would_create.append(str(alias.relative_to(root)))
                continue
            alias.symlink_to(rel, target_is_directory=True)
            created.append(str(alias.relative_to(root)))

    for alias_root in ALIAS_ROOTS:
        base = root / alias_root
        if not base.is_dir():
            # Not bootstrapped yet is a state, not a defect: a real run creates it, and
            # --check already reported every alias it would create. Only a symlink that
            # points at nothing is actually broken.
            if not args.check:
                missing.append(alias_root)
            continue
        # Prune: an alias whose canonical source is gone is stale, not repairable, and a
        # tree that mirrors another must not keep entries the other has dropped. `broken`
        # means still broken after this run, so a successful prune does not appear in it.
        for entry in sorted(base.iterdir()):
            if not entry.is_symlink() or entry.exists():
                continue
            if args.check:
                missing.append(str(entry.relative_to(root)))
                would_prune.append(str(entry.relative_to(root)))
                continue
            entry.unlink()
            pruned.append(str(entry.relative_to(root)))

    ok = not missing
    result = {
        "ok": ok,
        "check": args.check,
        "root": str(root),
        "canonical": CANONICAL,
        "aliasRoots": list(ALIAS_ROOTS),
        "created": created,
        "repaired": repaired,
        "pruned": pruned,
        "skipped": skipped,
        "broken": missing,
        "wouldCreate": would_create,
        "wouldRepair": would_repair,
        "wouldPrune": would_prune,
        "timedOut": out_of_time(),
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        def n(a: list[str], b: list[str]) -> int:
            return len(b if args.check else a)
        print(f"root      : {root}")
        print(f"created   : {n(created, would_create)}")
        print(f"repaired  : {n(repaired, would_repair)}")
        print(f"pruned    : {n(pruned, would_prune)}")
        print(f"skipped   : {len(skipped)}  (already correct, or a real directory)")
        print(f"broken    : {len(missing)}")
        for b in missing:
            print(f"   BROKEN {b}")
        if args.check:
            print("CHECK ONLY - nothing was written")
        print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
