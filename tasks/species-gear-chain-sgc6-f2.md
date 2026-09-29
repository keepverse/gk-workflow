# SGC5-F2 — the owner ruling's premise is false: there is no generator to re-run

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the live corpus load has exactly ONE finding | `python -c "from seedsmith.adapters.actions.load import load_committed; ..."` | `FINDINGS: 1` — `unknown-family authored-basics.json act.attack \| act.attack: field 'atomFamilies' refused — unknown value 'atom.fx-overlay-damage'` | |
| the GENERATED corpus is already consistent with the registry | same script: every `atomFamilies` value across `committed-round-*.json` + `_rounds/**` + `authored-basics.json` checked against the 125 | only offender in the whole tree is that one row: `{"atom.fx-overlay-damage": [["authored-basics.json","act.attack"]]}` — **nothing to regenerate** | |
| the offending file is AUTHORED, not generator output | its own `_meta.authored` | "HAND-AUTHORED, not generator output. ... A generator must never write here, and a regeneration run must never overwrite it." | `gk-data/packs/fusion/data/seed/actions/authored-basics.json` |
| no generator writes it | `grep -rn "authored-basics" gk-forge/tools/seedsmith/seedsmith/ --include=*.py` | **no hit** — the only references are tests and `gk-core/src/FusionRpg.Server/Program.cs:749` (a reader) | |
| the id is a LIVE atom-registry family, not a retired affix family | atom-registry scan | `atom.fx-overlay-damage` is one of **31** families in `gk-data/packs/fusion/data/seed/atoms/*.json` (`gk-data/packs/fusion/data/seed/atoms/fx-core.json`: `family: atom.fx-overlay-damage`, `kind: resource.delta`, Overlay HP delta); the 125 affix families and those 31 are **disjoint** (overlap = 0) | |
| the owning spec names it deliberately | `docs/architecture/lawn-combat-wire/spec-basic-attack-seed.md:39`, `:95` | "`act.attack`, `kindHint: "basic"`, atom family `atom.fx-overlay-damage`"; "The authored brief's atom family resolves" | |
| the C# composer resolves it (so C# is green) | `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionCorpusImporterTests.cs:159` | seeds the REAL `gk-data/packs/fusion/data/seed/atoms/fx-core.json` and asserts `ImportedCount == 1`, `RejectedCount == 0` | |
| the two red rows, unchanged | `python -m pytest tests/test_cli.py tests/test_corpus_loader.py -q` | `2 failed, 43 passed` — both are this one finding (`test_actions_check_uses_domain_loader_and_excludes_round_scratch`, `ConfigFilesSurviveTests::test_loading_the_live_corpus_raises_no_findings_today`) | |
| the other 5 red rows are the same row | `python -m pytest tests/test_actions_description_completeness.py -q --tb=line` | ⚠ **CORRECTED 2026-09-23 (same lane, later the same day): the first pass asserted all 5 shared this row's cause. They do not.** 3 name `act.attack` (`test_every_real_committed_action_carries_provenance` — the row deliberately carries no `_provenance`; `test_load_committed_reports_zero_loader_findings` — the unknown family; `test_resumed_plan_is_empty_now_that_every_real_action_has_a_description` — which lists BOTH ids). 3 name a SECOND cause: `gk-data/packs/fusion/data/seed/actions/committed-round-1.json`'s `action.family.academic.004` has no inline `description` (only `descriptionKey`; measured — the ONE of 181 action-seed entries missing it) → `test_content_field_missing_is_clean_on_the_real_corpus`, `test_resumed_plan_is_empty...`, and `test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done` (whose name says "zero model calls" but which reaches a REAL model call because that row still has work — hence `RuntimeError: model call failed … <urlopen error timed out>` with no model running). Filed as **SGC5-F4** | |

**Why the ruled acceptance cannot pass as written.** The ruling says "re-run the generator ... so the
corpus derives from the registry that exists now" and "NOT restore the family — it was retired
deliberately". Both halves rest on a false premise: `atom.fx-overlay-damage` was never a retired
*affix* family, it is a live *atom-registry* family, and the only row naming it is hand-authored with
`_meta.authored` explicitly forbidding a generator from writing there. A regeneration run changes
nothing (the generated corpus already has zero unknown families).

**Two candidate fixes, both a spec/owner decision — hence `blocked`, not `done`.**
(a) lawn-combat-wire re-authors `act.attack`'s `atomFamilies` to a member of the 125 (a content
decision: which affix family the basic attack spends); or
(b) the actions program widens the `atomFamilies` contract — and `vocab.load_family_ids` /
`load.py:250` — to the **UNION** of the 125 affix families and the atom-registry families the C#
composer actually resolves against (`store.ListAtomsByFamily`, fed from `gk-data/packs/fusion/data/seed/atoms/*.json`
**and** `gk-data/packs/fusion/data/seed/atoms/generated/*.json`).

⚠ **Option (b) was published WRONG the first time and is corrected here (2026-09-23, same lane).**
The first form said "widen to the full atom-family corpus the C# composer resolves against", implying
that set CONTAINS the 125. Measured, it does not — the two namespaces are largely disjoint:

| Candidate accepted set | size | families the committed corpus uses that it would REFUSE |
|---|---|---|
| today: the 125 affix families (`gk-data/packs/fusion/data/seed/items/affix-families/*.json`) | 125 | **1 family / 1 row** — `atom.fx-overlay-damage`, this row |
| (b) as first published: the atom-registry families (`gk-data/packs/fusion/data/seed/atoms/*.json` 31 + `gk-data/packs/fusion/data/seed/atoms/generated/*.json` 74) | 105 | **60 families / 205 rows** — it would break the corpus |
| (b) corrected: the UNION | 169 | **0 families / 0 rows** |

So the union is the only form of (b) that admits this row's id without refusing anything the corpus
already uses; the atom-registry set alone (overlap with the 125 is only 61) would have been a silent
regression of 205 rows. Both numbers are reproduced by a scan of the four `committed-round-*.json`
plus `authored-basics.json`.

This is the same question `gk-forge/tools/seedsmith/tests/test_coverage_report.py:888` NOTED on 2026-09-15 and
left open ("whether a hand-authored basic may spend a non-98 atom id is the action program's spec
question, not this generator's").

## Correction 2026-09-23 (same lane, later the same day) — this row accounts for 3 of the 8 red rows, not 5

The row above (corrected once already) ends by saying the 5 `knownRed` rows split 3 to this row and 3 to
SGC5-F4. That split then moved once more, because the same pass corrected the over-broad contract behind
one of those attributions:

* `test_every_real_committed_action_carries_provenance` required a `description_backfill` `_provenance`
  on EVERY `action-seed` row — including the authored `act.attack`, whose file states it "Deliberately
  carries no `_provenance` block" as the marker separating authored content from generator output. It now
  asserts the split contract (generated rows: `description` + provenance; authored rows: a description and
  **no** provenance) and keeps its name, so its `knownRed` entry stays valid. It still fails — on SGC5-F4's
  real gap (`action.family.academic.004` has no description), not on this row.
* `plan()` targeted the authored row too (measured `['act.attack', 'action.family.academic.004']`), so a
  real `backfill` run would have written into `authored-basics.json`. `is_authored` now excludes it; the
  plan reads `['action.family.academic.004']`.

**Post-correction split of the 5 `knownRed` rows:** 1 names this row
(`test_load_committed_reports_zero_loader_findings`) and 4 name SGC5-F4
(`test_content_field_missing_is_clean_on_the_real_corpus`, `test_every_real_committed_action_carries_provenance`,
`test_resumed_plan_is_empty_now_that_every_real_action_has_a_description` — which now lists ONLY
`action.family.academic.004` — and `test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`).
So this row's cause accounts for **3 of the program-wide 8**: these 2 plus that 1.
