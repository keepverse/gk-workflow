# Task 4 — anchor regen + byte-identical rerun

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 4. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §1, §4.
Code added (the task's Files line said "regen only", but **no regen mechanism existed** — see below):
`run/runner.py` (`refresh_rank`, deterministic, rank-only), `report/cli.py` (`creatures run refresh-rank`
+ dispatch/help/`--dry-run`), `tests/test_run_runner.py`. Data: `gk-data/packs/fusion/data/seed/creatures/species/**` (549
files, 904 entries) — regen output, no hand edits.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every resolved anchor carries the table's rank | `python - <<'PY' … derive_rank over gk-data/packs/fusion/data/seed/creatures/species/** … PY` | **904 anchors / 904 carry a `rank` key / 904 equal `derive_rank(own threatBand, own rarity)` / `_derived` lists `rank` in 904** | `gk-data/packs/fusion/data/seed/creatures/species/**` |
| Unresolved → not defaulted | `python -m pytest tests/test_run_runner.py -q -k "refresh_rank"` (in `gk-forge/tools/seedsmith`) | green — `test_refresh_rank_never_defaults_an_unresolved_input` plants `threatBand="unresolved"` and a fabricated `chaff`, and the pass writes `"unresolved"` | `tests/test_run_runner.py` |
| Rerun over unchanged anchors byte-identical | `python -m seedsmith creatures run refresh-rank` (twice) | **second run: `0 rank value(s) refreshed`; tree sha256 `cd1ffeb42c342a09865016527af660646267db2814a92a539a9033f10545af1d` before AND after** | — |
| `--check` green post-regen | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | `--check: clean, 904 species match …\data\generated\creatures` (rank is not in the concrete schema yet — Task 6) | — |
| Regen diff reviewed | `python - <<'PY' … compare HEAD vs working tree per entry … PY` | **549 files / 904 entries / 0 unexpected differences**: `rank` added 904, `_derived` gains exactly `rank` 904, `_provenance.emittedUtc` moved 904, `relead` preserved 104; no file added or deleted | — |
| Generated-tree guard | `python gk-core/scripts/guard-generated-seed.py` | `clean (552 changed file(s) inspected)` | — |
| Anchor-reading C# tests | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~SpeciesExpander\|FullyQualifiedName~Encounter\|FullyQualifiedName~EligibilityAxis\|FullyQualifiedName~SpeciesRollPreview\|FullyQualifiedName~CreatureRank"` | **Passed! — Failed 0, Passed 277, Total 277, 4 s** | — |
| Seedsmith (anchor + runner + corpus) | `python -m pytest tests/test_anchor_contract.py tests/test_anchor_derive.py tests/test_anchor_emit.py tests/test_species_kind_and_measured_basis.py tests/test_classify_pipelines.py tests/test_run_orchestrator.py tests/test_run_runner.py tests/test_creatures_completeness.py tests/test_creature_metrics.py tests/test_adapter_creatures.py -q` | **215 passed in 28.81 s** | — |
| The task's own filter | `python -m pytest tests/ -q -k "anchor or rank"` | **191 passed, 1 skipped, 4177 deselected, 1176 subtests passed, 10.70 s** | — |

## NOT proved / findings

- **Task 4's premise was wrong and the regen mechanism is this commit's real deliverable.** No
  deterministic corpus-wide re-emit pass existed: `fix_unresolved` skips an already-resolved field,
  `rederive_from_measured_capture` skips an unchanged basis/speciesKind, `fix_secondary_from_fusion_lineage`
  only reads fusion recipes — so none can put a field on a corpus that already has every classified field
  resolved. `refresh_rank` is that pass (module 9 `run-control`, beside its three siblings), reached by
  `python -m seedsmith creatures run refresh-rank`. Recorded as a `decision` note.
- **Defect found and fixed in the same commit (in this lane's own fence, not filed as a row):** the
  `_write_species_entry` merge branch built a fresh `AnchorProvenance(...)` and dropped
  `_provenance.relead` — `lead-relabel-pass`'s record — from every entry any deterministic pass rewrote.
  Measured live: the first regen lost it on **104 of 904** entries. `run/runner.py:312` now carries
  `ReleadProvenance.from_dict(old_relead)` through, with a regression test.
- The corpus has **0** `"unresolved"` ranks today (all 904 pairs are resolved), so "unresolved → absent" is
  proven by the unit test, not by a real anchor. The distribution is a reading, not a claim:
  `fused 486 · cultivated 159 · chimeric 67 · heirloom 49 · sprout 45 · chaff 34 · grafted 33 · almanac 23 ·
  firstseed 4 · sunwoven 4`.
- "Unresolved → absent" is satisfied as an absent **value**: Python writes the `"unresolved"` string (spec §1)
  and C# maps it to `null`; `emit.entry_for`'s own rule is that an unresolved field is never omitted.
- The first regen moves `_provenance.emittedUtc` on the 904 touched entries — the merge path's established
  behaviour for every deterministic pass, and the reason a second run is a true no-op (skipped entries are
  never rewritten). Not a byte-identical claim about the first run.
- `gk-data/packs/fusion/data/generated/creatures/**` is untouched: rank reaches it only once `SpeciesExpander`/
  `ConcreteSpecies` can carry it (Tasks 5-6), which is GAP-2's own correction.
- Task 4's `Files:` line named only the anchor tree; the code addition is a deliberate, recorded deviation.
