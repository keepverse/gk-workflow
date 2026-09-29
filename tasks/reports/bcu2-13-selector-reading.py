#!/usr/bin/env python3
"""BCU2.13's selector reading, model-free.

BCU2.13 is "re-classify the remaining `elementSecondary` gap (the register says 127 species; the
manager's 2026-09-23 board reads 108) + `species-build doublecherry attackTempo`". It runs as a
manager-run model job whose outputs are `gk-data/packs/fusion/data/seed/creatures/**` — outside lane `cmdc/bcu8-4`'s fence.
This script records the BEFORE/after reading those outputs change, with no model calls and no writes:

    PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-13-selector-reading.py
    ... --out tasks/reports/bcu2-13-selector-reading.json

Selector (the manager's own definition, `2004b5a42`): species whose `elementSecondary` is `none` **and**
that no fusion recipe names as an output. The second half is what separates the real gap from the 262
species that are legitimately `none` (`tasks/combat-unification-todo.md` F2b's own reading).

`attackTempo` half: the `doublecherry` anchor's field and its `_provenance.confidence.attackTempo` —
`tasks/species-build-todo.md` records that a real classify-pipeline value is owed there (no
deterministic fallback, unlike `threatBand`/`rarity`/`aptitudePrimary`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECIES_ROOT = REPO_ROOT / "data" / "seed" / "creatures" / "species"
RECIPES_PATH = REPO_ROOT / "data" / "generated" / "creatures" / "_fusion-recipes.json"


def load_anchors() -> dict[str, dict]:
    """One anchor per roster species — resolved by `speciesId`, NEVER by row position.

    The anchors live in FAMILY files that hold many rows (`zombie/undead.json` holds 63), and
    `_index.json` maps a species to its family, not to a row. Taking `rows[0]` therefore reads the
    family's base species for every key that is not first — measured 2026-09-23: **355 of 904** keys
    were read as somebody else's anchor before this was fixed, which is the same id-space class of bug
    the register's own note warns about. Every key resolves exactly, and no file repeats a `speciesId`.
    """
    index = json.loads((SPECIES_ROOT / "_index.json").read_text(encoding="utf-8"))
    anchors: dict[str, dict] = {}
    for species_id, rel in index.items():
        rows = json.loads((SPECIES_ROOT / rel).read_text(encoding="utf-8"))
        match = next((row for row in rows if row.get("speciesId") == species_id), None)
        if match is None:
            raise SystemExit(f"no anchor row for {species_id!r} in {rel} — the index and the family "
                             f"files disagree; refusing to read a neighbour's anchor")
        anchors[species_id] = match
    return anchors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)

    anchors = load_anchors()
    recipes = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    # The id spaces differ by case: `_index.json` keys are CamelCase (`AcientSunNut`) while the
    # recipes name their outputs in lower case (`acientsunnut`). Comparing them raw makes every
    # species look unnamed — the exact second wrong selector `2004b5a42` names and rejects.
    outputs = {str(row["outputSpeciesId"]).lower() for row in recipes.values()}
    inputs = {str(row.get(key, "")).lower()
              for row in recipes.values() for key in ("inputSpeciesIdA", "inputSpeciesIdB")}

    none_secondary = sorted(s for s, a in anchors.items() if is_none(a.get("elementSecondary")))
    selector = sorted(s for s in none_secondary if s.lower() not in outputs)
    # Three readings the register/board figures can be compared against, named rather than implied:
    #   A the manager's stated rule (none AND no recipe names it as an OUTPUT)
    #   B also excluding species a recipe uses as an INPUT (they have a lineage, just not an output)
    #   C A restricted to `pure` species (no fusion ancestor at all)
    def _count(pred) -> int:
        return len([s for s in none_secondary if pred(s)])

    def _distribution(members: "list[str]") -> dict:
        """Where the gap sits, so the owner's content call has the shape of it, not just a total."""
        import collections

        def field(s, key):
            value = anchors[s].get(key)
            if isinstance(value, (list, tuple)):
                return "+".join(str(v) for v in value)
            return str(value) if value is not None else "(absent)"

        return {
            "bySide": dict(collections.Counter(field(s, "side") for s in members)),
            "byPure": dict(collections.Counter(field(s, "pure") for s in members)),
            "byRarity": dict(collections.Counter(field(s, "rarity") for s in members)),
            "byFamily": collections.Counter(field(s, "family") for s in members).most_common(3),
        }

    variants = {
        "A_none_and_not_a_recipe_output": _count(lambda s: s.lower() not in outputs),
        "B_also_not_a_recipe_input": _count(lambda s: s.lower() not in outputs and s.lower() not in inputs),
        "C_A_restricted_to_pure": _count(lambda s: s.lower() not in outputs and anchors[s].get("pure")),
    }
    tempo = anchors.get("DoubleCherry") or anchors.get("doublecherry")

    reading = {
        "reading": "BCU2.13 selector + doublecherry attackTempo, model-free (no writes)",
        "repoHead": _head(),
        "elementVocabulary": _element_envelope(anchors),
        "speciesInIndex": len(anchors),
        "fusionRecipeCount": len(recipes),
        "speciesWithNoneSecondary": len(none_secondary),
        "selectorElementSecondaryGap": len(selector),
        "selectorVariants": variants,
        "selectorSample": selector[:10],
        "selectorMembers": selector,
        "selectorMembersVariantB": sorted(s for s in none_secondary if s.lower() not in outputs and s.lower() not in inputs),
        "selectorMembersVariantC": sorted(s for s in none_secondary if s.lower() not in outputs and anchors[s].get("pure")),
        "noneSecondaryMembers": none_secondary,
        "selectorDistribution": _distribution(selector),
        "noneSecondaryDistribution": _distribution(none_secondary),
        "registerReading20260907": 127,
        "boardReading20260923": 108,
        "doublecherry": None if tempo is None else {
            "attackTempo": tempo.get("attackTempo"),
            "confidence": (tempo.get("_provenance") or {}).get("confidence", {}).get("attackTempo"),
            "promptVersions": (tempo.get("_provenance") or {}).get("promptVersions"),
        },
    }
    dump = json.dumps(reading, indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(dump, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(dump, end="")
    return 0


def _element_envelope(anchors: dict[str, dict]) -> dict:
    """The closed element vocabulary, READ from the adapter (never transcribed), tallied against the
    corpus: a `none` secondary is the gap F2b is about, but a value *outside* the vocabulary would be a
    different, worse finding — so the reading states which one this is.

    `schemas`' own source note pins the vocabulary to `gk-core/src/FusionRpg.Core/Combat/Element/ElementTable.cs:125-130`.
    """
    import collections
    import sys

    sys.path.insert(0, str(REPO_ROOT / "tools" / "seedsmith"))
    try:
        from seedsmith.adapters.creatures.anchor.prompts import ELEMENTS
    except ImportError:  # pragma: no cover - environment, not logic
        return {"error": "seedsmith creatures adapter not importable"}
    vocabulary = sorted(str(e) for e in ELEMENTS)
    primary: collections.Counter = collections.Counter()
    secondary: collections.Counter = collections.Counter()
    outside: list[dict] = []
    for species, anchor in anchors.items():
        for field, tally in (("elementPrimary", primary), ("elementSecondary", secondary)):
            value = str(anchor.get(field) or "(absent)")
            tally[value] += 1
            if value not in vocabulary and value not in ("none", "(absent)"):
                outside.append({"species": species, "field": field, "value": value})
    return {
        "vocabulary": vocabulary,
        "primary": dict(primary),
        "secondary": dict(secondary),
        "outsideVocabulary": outside,
        "speciesMissingPrimary": [s for s, a in anchors.items() if is_none(a.get("elementPrimary"))],
    }


def is_none(value) -> bool:
    return value is None or str(value).strip().lower() in ("", "none")


def _head() -> str:
    import subprocess

    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - environment, not logic
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
