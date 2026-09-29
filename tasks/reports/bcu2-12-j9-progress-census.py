#!/usr/bin/env python3
"""BCU2.12 / J9 — the species-corpus progress census, model-free.

J9's acceptance is *"840 trees × 40 nodes committed as catalog data (D45)"*, with the plan regenerating
byte-identically and the uniqueness gate holding corpus-wide. Its run is a manager-run model job in
flight (`tasks/run-board-20260920.md:1562`, `2004b5a42`), writing `gk-data/packs/fusion/data/seed/passive-tree/**`. This script
measures how far it has actually got, from the three places its progress lands, so a re-run after the run
gives the delta:

    python tasks/reports/bcu2-12-j9-progress-census.py
    ... --out tasks/reports/bcu2-12-j9-progress-census.json

  * `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json` — `done` keys are `<subject>:<nodeId>`, so
    a species' accepted-row count is its key count (the resume ledger, written before the seed document).
  * `gk-data/packs/fusion/data/seed/passive-tree/nodes/<speciesId>.json` — the committed tree; its `nodes` list is the count
    J9's acceptance measures against 40.
  * `gk-data/packs/fusion/data/seed/passive-tree/species/<speciesId>.json` — the metadata file J8/J9 write only when the
    codex sentence resolved (a species whose tree exists but whose codex did not resolve has no file —
    `_j9_batch_run.py:138`'s own documented outcome).

A species can be in the ledger with no node file: that is the run's own `startedIncomplete` shape, not a
lost tree. Writes nothing under `data/`.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER = REPO_ROOT / "data" / "seed" / "creatures" / "species" / "_index.json"
TREE_ROOT = REPO_ROOT / "data" / "seed" / "passive-tree"
LEDGER = TREE_ROOT / "_runs" / "tree-language.ledger.json"
NODES = TREE_ROOT / "nodes"
META = TREE_ROOT / "species"
NODES_PER_TREE = 40  # J9's own acceptance figure


def build() -> dict:
    roster = sorted(json.loads(ROSTER.read_text(encoding="utf-8")))
    done = json.loads(LEDGER.read_text(encoding="utf-8"))["done"]
    ledger_rows: dict[str, int] = {}
    ledger_name_keys: dict[str, collections.Counter] = {}
    for key, entry in done.items():
        subject = key.split(":", 1)[0]
        ledger_rows[subject] = ledger_rows.get(subject, 0) + 1
        name_key = (entry.get("record") or {}).get("nameKey")
        if name_key:
            ledger_name_keys.setdefault(subject, collections.Counter())[name_key] += 1

    def node_count(species: str) -> int | None:
        path = NODES / f"{species}.json"
        if not path.is_file():
            return None
        return len(json.loads(path.read_text(encoding="utf-8")).get("nodes", []))

    def codex(species: str) -> dict | None:
        path = META / f"{species}.json"
        if not path.is_file():
            return None
        doc = json.loads(path.read_text(encoding="utf-8"))
        return {"hasSummary": bool(doc.get("codexSummary")), "attempts": doc.get("codexAttempts"),
                "uniqueNodeIds": len(doc.get("speciesUniqueNodeIds") or [])}

    rows = []
    for species in roster:
        count = node_count(species)
        duplicates = {k: c for k, c in (ledger_name_keys.get(species) or {}).items() if c > 1}
        rows.append({
            "species": species,
            "ledgerAcceptedRows": ledger_rows.get(species, 0),
            "nodesOnDisk": count,
            "complete": count == NODES_PER_TREE,
            "duplicateNameKeys": len(duplicates),
            "duplicateNameKeySamples": sorted(duplicates)[:3],
            "metadata": codex(species),
        })
    started = [r for r in rows if r["ledgerAcceptedRows"] or r["nodesOnDisk"] is not None
               or r["metadata"] is not None]
    # `build_seed_document` refuses a tree whose records repeat a `nameKey` (nodegen/emit.py:246 ->
    # `assert_no_duplicate_name_keys`, emit.py:48-60) and the records are the ledger's, so a species
    # with a self-duplicate in its own rows can never be written until that node is re-asked or its
    # ledger row superseded — the repair PT-J9-F1 names.
    unfileable = [r["species"] for r in rows
                  if r["ledgerAcceptedRows"] and r["nodesOnDisk"] is None and r["duplicateNameKeys"]]
    return {
        "reading": "BCU2.12/J9 — species-corpus progress, model-free (no writes)",
        "repoHead": _head(),
        "rosterSpecies": len(roster),
        "j9AcceptanceTarget": 840,
        "nodesPerTreeExpected": NODES_PER_TREE,
        "speciesInLedger": sum(1 for r in rows if r["ledgerAcceptedRows"]),
        "speciesWithNodeFile": sum(1 for r in rows if r["nodesOnDisk"] is not None),
        "speciesWithMetadataFile": sum(1 for r in rows if r["metadata"] is not None),
        "speciesComplete": sum(1 for r in rows if r["complete"]),
        "speciesInLedgerWithoutNodeFile": sorted(r["species"] for r in rows
                                                 if r["ledgerAcceptedRows"] and r["nodesOnDisk"] is None),
        "unfileableByOwnDuplicateNameKey": unfileable,
        "completedFractionOfRoster": f"{sum(1 for r in rows if r['complete'])}/{len(roster)}",
        "rows": started,
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
        print(json.dumps({k: v for k, v in doc.items() if k != "rows"}, indent=1))
    else:
        print(dump, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
