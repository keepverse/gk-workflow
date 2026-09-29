#!/usr/bin/env python3
"""BCU2.13's `attackTempo` half, measured model-free.

The register's BCU2.13 names two halves: combat-unification F2b's `elementSecondary` selector, and
species-build's `doublecherry attackTempo`. This script sizes the second one across the whole roster, so
the row is judged on a reading rather than on a memory of it:

    python tasks/reports/bcu2-13-attacktempo-census.py
    ... --out tasks/reports/bcu2-13-attacktempo-census.json

For every species in `gk-data/packs/fusion/data/seed/creatures/species/_index.json` it reads the anchor's `attackTempo` and
`_provenance.confidence.attackTempo`. `deterministic-fallback` is the tag the owning program's row keeps
deliberately for "resolved by something other than a real LLM vote" (`tasks/species-build-todo.md`,
2026-09-07): the owner set `doublecherry`'s value by hand from the anchor's own emitted evidence and
stamped it as such rather than disguising it as a model judgement. Sizing the tag tells the row whether
that is one species or a population. Writes nothing under `data/`.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECIES_ROOT = REPO_ROOT / "data" / "seed" / "creatures" / "species"


def build() -> dict:
    index = json.loads((SPECIES_ROOT / "_index.json").read_text(encoding="utf-8"))
    tempo: collections.Counter = collections.Counter()
    confidence: collections.Counter = collections.Counter()
    fallback: list[dict] = []
    cache: dict[str, list[dict]] = {}
    for species in sorted(index):
        rel = index[species]
        if rel not in cache:
            cache[rel] = json.loads((SPECIES_ROOT / rel).read_text(encoding="utf-8"))
        # Resolve by `speciesId`: a family file holds many rows and the index names the file, not the
        # row (taking `rows[0]` reads the family's base species — wrong for 355 of 904 keys).
        anchor = next((row for row in cache[rel] if row.get("speciesId") == species), None)
        if anchor is None:
            raise SystemExit(f"no anchor row for {species!r} in {rel} — refusing to read a neighbour's")
        value = anchor.get("attackTempo")
        tag = ((anchor.get("_provenance") or {}).get("confidence") or {}).get("attackTempo", "(absent)")
        tempo[str(value or "(absent)")] += 1
        confidence[str(tag)] += 1
        if tag == "deterministic-fallback":
            fallback.append({"species": species, "attackTempo": value, "confidence": tag})
    return {
        "reading": "BCU2.13 — attackTempo and its provenance tag across the roster, model-free (no writes)",
        "repoHead": _head(),
        "rosterSpecies": len(index),
        "attackTempoValues": dict(tempo),
        "confidenceTags": dict(confidence),
        "deterministicFallbackCount": len(fallback),
        "deterministicFallback": fallback,
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
