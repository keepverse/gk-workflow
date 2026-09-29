#!/usr/bin/env python3
"""BCU2.12 / J13 — the prompt-version vintage of the 42 shared passive trees, read model-free.

J13's title targets regenerating the 42 shared trees "under `tree-language/2`" and its third acceptance
clause asks every regenerated document to carry that version. This script measures what the committed
documents actually carry, so the row's target can be restated from a reading rather than a memory
(`tasks/passive-tree-todo.md` PT-J9-F2 raised exactly this, with an older reading of 22/4/21).

    python tasks/reports/bcu2-12-vintage-reading.py
    ... --out tasks/reports/bcu2-12-vintage-reading.json

Reads, per shared tree document (`gk-data/packs/fusion/data/seed/passive-tree/nodes/<tree>.json`):
  * the file-level `_provenance.promptVersion` (`mixed` means the file's nodes disagree), and
  * the node-level `promptVersion` tally — older rows simply lack the field, which is why a `mixed` file
    is not necessarily two labelled vintages.
and prints `PROMPT_VERSION` from the code that writes new ones (`nodegen/brief.py`), so target and
corpus can be compared in one reading. Writes nothing under `data/`.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_GLOB = REPO_ROOT / "data" / "generated" / "passive-tree" / "*.json"
NODE_DIR = REPO_ROOT / "data" / "seed" / "passive-tree" / "nodes"
BRIEF = REPO_ROOT / "tools" / "seedsmith" / "seedsmith" / "adapters" / "trees" / "nodegen" / "brief.py"


def prompt_version_in_code() -> str | None:
    match = re.search(r'^PROMPT_VERSION\s*=\s*"([^"]+)"', BRIEF.read_text(encoding="utf-8"), re.M)
    return match.group(1) if match else None


def build() -> dict:
    plans = {os.path.basename(p)[:-5] for p in glob.glob(str(PLAN_GLOB))}
    shared = sorted(t for t in plans if (NODE_DIR / f"{t}.json").is_file())
    file_vintage: collections.Counter = collections.Counter()
    node_vintage: collections.Counter = collections.Counter()
    mixed: list[dict] = []
    for tree in shared:
        doc = json.loads((NODE_DIR / f"{tree}.json").read_text(encoding="utf-8"))
        file_vintage[(doc.get("_provenance") or {}).get("promptVersion", "(absent)")] += 1
        tally = collections.Counter(str(n.get("promptVersion") or "(absent)")
                                    for n in doc.get("nodes", []))
        for version, count in tally.items():
            node_vintage[version] += count
        if len(tally) > 1:
            mixed.append({"tree": tree, "nodes": dict(tally)})
    return {
        "reading": "BCU2.12/J13 — shared-tree prompt-version vintage, model-free (no writes)",
        "repoHead": _head(),
        "sharedTrees": len(shared),
        "planTrees": len(plans),
        "planTreesWithoutNodeFile": sorted(plans - set(shared)),
        "nodeFilesWithoutPlan": sorted(os.path.basename(p)[:-5]
                                       for p in glob.glob(str(NODE_DIR / "*.json"))
                                       if os.path.basename(p)[:-5] not in plans),
        "promptVersionInCode": prompt_version_in_code(),
        "fileLevelPromptVersion": dict(file_vintage),
        "nodeLevelPromptVersion": dict(node_vintage),
        "filesWithMixedNodeVintage": len(mixed),
        "mixedSamples": mixed[:4],
    }


def _head() -> str:
    import subprocess

    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - environment, not logic
        return "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    doc = build()
    dump = json.dumps(doc, indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump, encoding="utf-8")
        print(f"wrote {args.out}")
    print(json.dumps(doc, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
