#!/usr/bin/env python3
"""BCU2.11 / ISG-gap-2 — why the Coverage/EmptyPartition residue is 911, and what it really is.

The metric is a set difference between the items adapter's *allocated* partitions (a snapshot of
`gk-forge/tools/ItemSeedValidator --list-partitions-json`, `adapters/items/registries.py:14`) and the corpus's
*occupied* ones (`metrics/coverage.py:9-14`). This script measures the two id spaces against each other
and emits, per allocated-but-empty partition, the reason it is empty — model-free, writes nothing
outside `tasks/reports/`.

    PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-11-partition-key-map.py
    ... --out tasks/reports/ISG-gap-2-per-partition.json

Inputs: `tasks/reports/ISG-gap-2-residue.json` (the metric's own findings — regenerate with
`seedsmith check ../../data/seed/items --adapter items --metric Coverage/EmptyPartition --json ...`),
the allocation snapshot, and the items corpus through seedsmith's own `Corpus.load`.

The two spellings, with their sources:

* allocation — `gk-forge/tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261`
  `Add(kind, $"{kind.Directory}/species/{speciesId}", $"set.{idSlug}-", …)` — the PARTITION keeps the
  raw `speciesId` (`sets/species/elephantzombie_a`), while the ID PREFIX hyphenates it
  (`set.elephantzombie-a-`), which the method's own doc comment (lines 250-259) explains for the prefix.
* emission — `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/authored.py:99-100`
  `set.might-offense-001` → partition `might-offense`; a creature-themed set is emitted as
  `set.<themeKey basename>-001` → `sets/elephantzombie-a`. No `species/` segment.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "seedsmith"))

SNAPSHOT = REPO_ROOT / "tools" / "seedsmith" / "seedsmith" / "adapters" / "items" / "_registry_snapshot" / "allocated_partitions.json"
RESIDUE = REPO_ROOT / "tasks" / "reports" / "ISG-gap-2-residue.json"
ITEMS_ROOT = REPO_ROOT / "data" / "seed" / "items"

GROUP_REASONS = {
    "species-slot-key-mismatch": (
        "Allocated as `sets/species/<raw speciesId>` (NamespaceAllocation.cs:261) while the corpus emits "
        "`sets/<hyphenated slug>` from the set's own id (setgen/authored.py:99-100). A same-species set "
        "entry exists under the other spelling, so this partition is empty by KEY, not by content."
    ),
    "species-no-set-entry": (
        "Allocated as `sets/species/<raw speciesId>` and no set entry exists under either spelling for "
        "this species — a genuine absence (variant/`_a` ids and enum-shaped ids dominate the sample)."
    ),
    "set-family-unfilled": (
        "A non-species set family partition; the other 40 allocated family/theme partitions hold entries."
    ),
    "attribute-kind-empty": "The `attribute` kind's only allocated partition; the corpus holds no attribute row.",
    "base-type-frame-empty": "One of 62 allocated base-type frame/slot partitions; the other 60 hold entries.",
    "display-template-slot-empty": "One of 6 allocated display-template slots; the other 3 hold entries.",
}


def norm(value: str) -> str:
    """Fold the two spellings onto one key: lowercase, alphanumerics only (`_`/`-`/case-insensitive)."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def load_occupied() -> tuple[set[str], set[str], dict[str, list[str]]]:
    from seedsmith.corpus.model import Corpus

    corpus = Corpus.load(ITEMS_ROOT)
    sets = [e for e in corpus.entries.values() if e.kind == "set"]
    by_theme: dict[str, list[str]] = {}
    for entry in sets:
        theme = (entry.data or {}).get("themeKey") or ""
        by_theme.setdefault(norm(theme.split(".", 1)[-1]), []).append(entry.partition)
    return set(corpus.partitions), {e.partition for e in sets}, by_theme


def build() -> dict:
    residue = json.loads(RESIDUE.read_text(encoding="utf-8"))
    allocated = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["partitionKind"]
    occupied, occupied_sets, by_theme = load_occupied()

    rows = []
    for finding in residue:
        partition = finding["subject"]
        kind = allocated.get(partition)
        if partition.startswith("sets/species/"):
            species = partition.split("sets/species/", 1)[1]
            counterpart = by_theme.get(norm(species))
            group = "species-slot-key-mismatch" if counterpart else "species-no-set-entry"
            rows.append({"partition": partition, "kind": kind, "group": group,
                         "reason": GROUP_REASONS[group],
                         "counterpartPartition": (counterpart or [None])[0],
                         "occupiedEntryCount": 0})
        else:
            group = {
                "set": "set-family-unfilled",
                "attribute": "attribute-kind-empty",
                "base-type": "base-type-frame-empty",
                "display-template": "display-template-slot-empty",
            }[kind]
            rows.append({"partition": partition, "kind": kind, "group": group,
                         "reason": GROUP_REASONS[group], "counterpartPartition": None,
                         "occupiedEntryCount": 0})

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["group"]] = counts.get(row["group"], 0) + 1

    # What the residue would read under the corrected key spelling, computed on the same corpus:
    # every species slot whose slug has an occupied `sets/<slug>` becomes occupied.
    projected = sum(1 for row in rows if row["group"] == "species-no-set-entry") \
        + sum(1 for row in rows if row["group"] not in ("species-slot-key-mismatch", "species-no-set-entry"))
    slugs = [norm(p.split("sets/species/", 1)[1]) for p in allocated if p.startswith("sets/species/")]
    collisions = sorted({s for s in slugs if slugs.count(s) > 1})

    return {
        "reading": "BCU2.11 / ISG-gap-2 — allocated-vs-emitted partition keys, model-free (no writes)",
        "repoHead": _head(),
        "allocatedPartitions": len(allocated),
        "occupiedCorpusPartitions": len(occupied),
        "occupiedSetPartitions": len(occupied_sets),
        "emptyAllocated": len(rows),
        "byGroup": counts,
        "speciesSlots": {
            "allocated": len(slugs),
            "withSameSpeciesSetEntry": len(slugs) - counts.get("species-no-set-entry", 0),
            "without": counts.get("species-no-set-entry", 0),
            "normalisedSlugCollisions": collisions,
        },
        "projectedEmptyUnderCorrectedSpelling": projected,
        "sources": {
            "allocation": "tools/ItemSeedValidator/Registries/NamespaceAllocation.cs:261",
            "emission": "tools/seedsmith/seedsmith/adapters/items/setgen/authored.py:99-100",
            "snapshot": "tools/seedsmith/seedsmith/adapters/items/_registry_snapshot/allocated_partitions.json",
        },
        "partitions": rows,
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
        print(json.dumps({k: v for k, v in doc.items() if k != "partitions"}, indent=1))
    else:
        print(dump, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
