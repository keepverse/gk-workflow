# ISG2 — combogen's grant vocabulary must be the real production atom catalog

Sub-agent task `item-seed-gen`. Second finding cleared; the first (`ISG1`) was the validator-side
artefact scan.

## The defect

`combogen.granted_family_vocabulary()` and `combogen.deps.preflight`/`validate_entries` closed
`grants[]` against `registries.load_atom_families()`, which globs **all** of `gk-data/packs/fusion/data/seed/atoms/**`:
the `FamilyExpansion` output (`generated/family-expand.*.json`) *plus* separate hand-authored atom
sources — `aura-content.json` (`atom.aura-*`), `fx-*.json` (`atom.fx-*`), `patron-aura.json`,
`trait-critical-hunter.json`, `extend-slot.json` — that no affix family carries.

The real production atom catalog is the one `GemContainerBuild`'s own doc names
(`gk-core/src/FusionRpg.Core/Items/Gems/GemContainerBuild.cs:24-33`): `gk-data/packs/fusion/data/seed/items/affix-families/**`
expanded through `FamilyExpansion.Expand`, "NOT the separate, much smaller
`gk-data/packs/fusion/data/seed/atoms/generated/*.json` snapshot". The same file is what `spec-combination-regen.md`
("Why 26 cells block") calls *"the **atom catalog** — `gk-data/packs/fusion/data/seed/items/affix-families/**` expanded by
`FamilyExpansion`"*. In id terms that is `registries.load_authored_affix_family_ids()`.

Measured cause: SSH2.5's `--retry-blocked` regen (`12e41658c`) introduced the 19 live
`ReferenceUnresolved` grants (`atom.aura-composure`, `-precision`, `-retribution`, `-onslaught`,
`-pierce`, `atom.fx-icd-butter`, `atom.fx-overlay-damage`) while `items validate --deps` stayed
green, because the preflight used the same over-broad set. Pre-`12e41658c` both shapes carried
**zero** bad grants (checked with `git show 12e41658c^:gk-data/packs/fusion/data/seed/items/combinations/*.json`).

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` — `granted_family_vocabulary()`
  returns `registries.load_authored_affix_family_ids()`.
- `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py` — `preflight` and `validate_entries`
  default to the same loader.
- `gk-forge/tools/seedsmith/tests/test_combogen.py` — new
  `test_the_offered_grant_vocabulary_is_the_production_atom_catalog` (contract, not a count: the
  offered set equals the authored affix-family ids, and its intersection with the atom-only
  families `load_atom_families() - load_authored_affix_family_ids()` is empty, so a silent revert
  fails loudly). `_first_real_external_grant` reads the same loader.

No seed JSON was touched. The already-shipped bad grants still need regeneration through the
generator; that is ISG3/ISG4, and it is why the validator count does not move in this commit.

**Correction (ISG5):** replacing `granted_family_vocabulary`'s body moved it from `run.py:79` to
`run.py:80`, and the `preflight` grant closure from `deps.py:85` to `deps.py:112` (`run.py:105`'s
tuning-ceiling line moved to 125). Four `strain-splice-host` doc citations now point at the wrong
line; `docs/**` is outside this session's allowed paths, so the re-anchor is filed as SSH2.9 in
`tasks/strain-splice-host-todo.md` instead of done here.

## Verification

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The combogen suite is green | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q` | pass — 89 passed | stdout |
| The 19 offending families are no longer offered | new guard test asserts `granted ∩ (load_atom_families() - load_authored_affix_family_ids()) == {}` | pass | `test_combogen.py` |
