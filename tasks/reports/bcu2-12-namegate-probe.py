#!/usr/bin/env python3
"""BCU2.12 — does the node gate actually refuse a name another subject already holds?

The corpus holds **12 nodes named `Kinetic Recirculation`** (byte-identical strings, distinct `nameKey`s
suffixed `-2`, `-4`, … `-13`, one pair inside `BigGatling`), while `build_response_gate`'s own docstring
says *"the name is checked against every OTHER subject's committed name, corpus-wide … a same-name draft
from a different tree is exactly the measured defect"* and `metrics/passive_tree.py`'s `NameCollision`
reports 388/1679 nodes as colliding. Either the gate refuses that shape (and the accepts came from a run
whose `taken_names` did not hold the earlier copies) or it does not (and the check is not wired the way
its docstring says).

This probe calls the real functions with no model and no corpus writes:

    PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-12-namegate-probe.py

  * `build_response_gate(..., taken_names=["Kinetic Recirculation"])` over a draft with that name —
    does it return `name_collision`'s problem? (with a control: the same draft against an unrelated
    taken name, which must pass)
  * `_derive_unique_name_key` — does it suffix the key on a collision (which is where `-2`, `-4`, … come
    from), and does it touch the NAME at all?
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "seedsmith"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "seedsmith" / "tests" / "adapters" / "trees"))

from seedsmith.adapters.trees.nodegen import run  # noqa: E402
from seedsmith.adapters.trees.nodegen.schema import schema_for_call  # noqa: E402
from seedsmith.adapters.trees.nodegen.vocab import AffixOption, AffixVocabulary  # noqa: E402

AFFIX_A = AffixOption(affix_id="atom.a", name="Alpha Strike", tags=("offensive",), kind_id="k1")
AFFIX_B = AffixOption(affix_id="atom.b", name="Bulwark", tags=("defensive",), kind_id="k2")
VOCAB = AffixVocabulary(options=(AFFIX_A, AFFIX_B))
TAKEN = "Kinetic Recirculation"


def response(name: str, name_key: str = "tree.node.kinetic-recirculation") -> dict:
    return {
        "affixIds": ["atom.a"], "affinity": ["core"],
        "exclusion": {"form": "none", "propertyKeys": []},
        "name": name, "nameKey": name_key, "flavor": "A steady line.",
        "rationale": "", "blocked": "",
    }


def gate_with(taken_names: list[str]):
    schema = schema_for_call(["atom.a", "atom.b"], ["posture"])
    return run.build_response_gate(
        schema=schema, permitted_affix_ids=["atom.a", "atom.b"],
        permitted_property_keys=["posture"], anti_motif_tags=[], affix_vocab=VOCAB,
        property_vocabulary={"posture": ("vanguard", "warden")},
        tree_display_name="Might", motifs=["strength"], taken_names=taken_names)


def build() -> dict:
    duplicate = gate_with([TAKEN])(response(TAKEN))
    control = gate_with(["Some Other Name"])(response(TAKEN))
    key_derivation = {
        name: run._derive_unique_name_key(name, {"tree.node.kinetic-recirculation"})
        for name in (TAKEN, "Fresh Phrase")
    }
    return {
        "reading": "BCU2.12 — the node gate's name-collision behaviour, model-free (no model, no writes)",
        "repoHead": _head(),
        "gateWithTakenName": {"problems": duplicate,
                              "refused": bool(duplicate),
                              "namesTheCollision": any("already used" in p for p in duplicate)},
        "controlWithUnrelatedTakenName": {"problems": control, "passed": not control},
        "deriveUniqueNameKey": key_derivation,
        "nameKeySuffixed": key_derivation[TAKEN] != key_derivation["Fresh Phrase"],
    }


def _head() -> str:
    import subprocess

    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # pragma: no cover - environment, not logic
        return "unknown"


def main() -> int:
    print(json.dumps(build(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
