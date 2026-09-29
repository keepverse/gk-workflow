# ISG-gap-1 — the hybrid-role SetCompletability GAPs, fixed in the generator (closed 2026-09-21)

Root cause, read not inferred: the five `sets-1c` partitions (`_meta.model` claude-sonnet-5,
`promptVersion` 1, `authoredUtc` 2026-08-22) predate D30 by thirteen days and declare
`registryVersions.core: 1`. The forward cap is already correct — `setgen/brief.py:13,129` prints only
`roles.HYBRID_CORE_ROLES` to the model and `setgen/distribute.py:182` refuses the rest — so **no
`set-charm-gen/*` partition can carry this defect**, and the five legacy partitions are never planned
again (`setgen/run.py:224-228`: the planning pool is species + build themes, and the legacy
`theme.*` ids enter only as the id-collision set `setgen/themes.py:125` publishes). What was missing is a VALIDATION on
already-shipped rows plus the backward pass every sibling set-shape defect already has
(`repair_sets`/`repair_species_ids`/`repair_set_classes`/`repair_names`). Those five partitions are
`theme.*`, so `items fill` cannot repair them either.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Baseline reproduced at base | `cd gk-forge/tools/seedsmith && python -m seedsmith check ../../data/seed/items --adapter items` | exit `1`, `961 gap, 607 note, 153 not_measured`; **30** of them `[GAP] Linkage/SetCompletability` | row `ISG-gap-1` |
| The defect population, measured | `python` walk of `gk-data/packs/fusion/data/seed/items/sets/**` for `role in {ward-array,head-guard,sense}` | **18 entries / 5 files / 30 member rows** (15 `head-guard` + 15 `sense`) — every one `batch: sets-1c`; 0 anywhere else in 910 entries | `gk-data/packs/fusion/data/seed/items/sets/{verdant-graft,rusted-legion,frostbitten-vanguard,sunwoven-almanac,thorned-chassis}.json` |
| Plan before the write | `python -m seedsmith items repair-set-roles` | `changedEntries 18, changedFiles 5, changedMembers 21, relocations 10 rows`, exit `0` | `setgen/role_repair.py` |
| Repair applied through the generator | `python -m seedsmith items repair-set-roles --write --allow-production-tree` | exit `0`, 5 partitions written, `299 insertions(+), 65 deletions(-)` | `git diff --stat gk-data/packs/fusion/data/seed/items/sets/` |
| Idempotent | the same command again | `changedEntries 0, changedFiles 0, changedMembers 0` | — |
| The metric is clean, exit 0 | `python -m seedsmith check ../../data/seed/items --adapter items --metric Linkage/SetCompletability` | `no findings`, **exit 0** | — |
| The full check, honestly | `python -m seedsmith check ../../data/seed/items --adapter items` | exit `1`: `931 gap, 607 note, 153 not_measured` — **0** `SetCompletability`; the 931 are the base corpus's own pre-existing `Coverage/EmptyPartition 911, Coverage/PairwiseHole 6, Quality/FlavourMissing 5, Content/FieldMissing 5, SemanticDedup/NearDuplicate 4`, which the unmerged `corpus/bcu211` fills | see erratum below |
| Structure preserved | `python` HEAD-vs-worktree count of the 5 files | `entries 30->30`, `memberRows 180->180`, `distinctRoles 26->26`, thresholds identical | — |
| New tests | `PYTHONPATH=. python -m pytest tests/test_role_repair.py -q` | `20 passed` | `gk-forge/tools/seedsmith/tests/test_role_repair.py` |
| The five named files, clean on HEAD | `PYTHONPATH=. python -m pytest tests/test_combogen.py tests/test_strain_splice_gen.py tests/test_materials_gen.py tests/test_recipes_gen.py tests/test_items_adapter.py -q` | baseline before the change: `224 passed, 26 subtests passed`; after: unchanged — **nothing failed on a clean HEAD** | — |
| Plus the setgen siblings | `PYTHONPATH=. python -m pytest tests/test_set_charm_gen.py tests/test_topology_repair.py tests/test_linkage.py -q` (all eight together) | `360 passed, 2709 subtests passed` | — |
| The C# validator still gates the corpus | `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items` | `PASS — 3978 entries across 1013 files, 2589 warnings.` | — |
| Path-owned verification | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(...) -Session item-seedgen-genfix"` | exit `1`; **my** file's doc-citation audit is clean (`D1 4 (0 HIGH), D2 0, D3 0`) after re-anchoring 5 dead citations; it aborts on the session-record DRIFT above, before its `test: guard` step | — |
| The module boundary, run in three bounded invocations (the unsplit run was interrupted twice at ~62%) | `PYTHONPATH=. python -m pytest tests/test_[a-i]*.py -q` · `tests/test_[j-z]*.py -q` · `tests/adapters tests/pipeline tests/workflow -q` | `2041 passed / 18 failed`, `1688 passed / 3 failed`, `585 passed / 1 failed` — 4314 passed, 22 failed, 3 skipped; **19 of the 22 are listed in `tasks/reports/seedsmith-baseline-e0f1375d.json`**, and the other 3 are the routed findings below | — |
| Guard suite (the step `verify-change.ps1` never reached) | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --nologo -v q` | `Failed: 3, Passed: 580, Total: 583` — all three name other lanes' files (routed below) | — |

## Acceptance erratum requested: the row's `exits 0` is not achievable on this branch

The row's acceptance reads *"`seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` exits 0"*. The BCU2.11
reading that produced the row was taken **on `corpus/bcu211`**, whose 68-file fill cleared the 931
`Coverage/EmptyPartition`/`Quality/FlavourMissing`/`Content/FieldMissing` gaps first — that is why the
manager saw `SetCompletability` as the only remaining GAP family. This lane is fenced to
`gk-forge/tools/seedsmith/**` + `gk-data/packs/fusion/data/seed/items/**` on a branch cut from `39029506f160`, which does **not**
carry bcu211, and the manager owns that merge. So the strongest check this lane can run is the same
metric on the same corpus — `--metric Linkage/SetCompletability` → `no findings`, exit `0` — plus the
full-check delta, which fell by exactly the 30 GAPs this task owns (961 → 931) and gained nothing. The
remaining 931 are named individually above and are all outside this lane's fence.

## Other hybrid sets with the same defect — a measured reading, not a guess

**18 of 910 shipped set entries** (5 of 885 files) claimed a role outside the hybrid core; all 18 are
in the `sets-1c` batch. After the fix: **0 of 910**, re-measured by walking the corpus and by
`test_no_shipped_set_entry_names_a_role_outside_the_hybrid_core`. The repair's own reading: 21
distinct-role relocations (`head-guard -> core-guard 2 / mantle 4 / girdle 2 / footing 1 / infusion 1`;
`sense -> manipulator 8 / jewel-major 3`) — 17 onto a host `core.v1.json`'s own `hybridDropReason`
names, 4 onto that role's nearest non-armament weight class because both its named hosts were already
claimed by the same entry. Every count here is printed by the tests and asserted only for closure.

## Out-of-fence findings, routed (owners are outside this lane's allowed paths)

- **`tasks/sessions/item-seedgen-genfix.json:7` carries a RELATIVE worktree path.**
  `docs/contributing/session-boundary.md:27` requires an absolute one, and
  `scripts/session-boundary-check.py:82-83` `Test-Path`s it, so from inside the worktree the record
  reads as DRIFT and `verify-change.ps1` aborts before its own `test: guard` step. Six other active
  records spell it the same way (the check lists them as non-blocking drift). Owner: whoever authors
  session records — **manager, please route**. Not fixable by this lane: `tasks/sessions/**` is
  outside its fence.
- **Stale `gk-core/tests/FusionRpg.Core.Tests/...` citations after the test-project split.** The merge's
  TVB5.7 split renamed the project to `gk-core/tests/FusionRpg.Core.Items.Tests`, so ~20 files under
  `docs/**` and `tasks/evidence-fragments/**` now carry dead paths (the `-Strict` audit lists
  `legion-build`, `npc-story-events`, `strain-splice-host` (×2, into `combogen/emit.py`, which is 175
  lines and cited at `:185`), `trade-network` and `world-stage`). The 5 in this lane's
  `tasks/item-seedgen-todo.md` are re-anchored here; the rest are other owners' files.
- **One real P1 population pin, not this lane's:** `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70`
  (`Assert.Equal(64, loaded.CombinationCorpusDigest.Length)` has no pin marker) is the single finding
  that makes `test_guard_population_pin.py`'s gating backlog non-zero. The file is untouched by this
  lane; it arrives from another lane's commit. Owner: server/combination.
- **`tests/adapters/trees/test_nodegen_vocab.py:29`** pins `tag_counts["utility"] == 19` and reads 17 —
  the known `g-evade` utility-tag removal (lane tvb58), pre-existing on this branch.
- **Three `gk-core/tests/FusionRpg.Guard.Tests` failures, all other owners':**
  `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`
  (pre-existing, lane tvb58), `ZombossCommanderLevelSingleReaderGuardTests` (names
  `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.EmpireSpecies.cs`, an empire-progression file), and
  `VerificationBoundaryWorkflowTests.Planner_accepts_an_explicit_path_within_the_active_session_scope`
  (fails on `backlog-recon-20260921`'s unresolvable worktree path).

## Not proved

- **The runtime consumer was not exercised.** No game launch, no `SetCorpus.Parse` run, no DB import.
  What was read: `SetCorpus.cs:124` accepts any *registered* role (so it accepted `head-guard`/`sense`),
  and `FrameMixPredicate.HybridCoreBudget` prices only `HybridEligible` roles. The claim that a hybrid
  cannot complete such a set is therefore read from code and from `ssot-sets.md` §3.7, **not observed
  in play**. This lane is a corpus/generator lane; the live probe belongs to whoever owns it.
- **A pre-existing validator gap, filed for routing (not this lane's to fix).**
  `gk-forge/tools/ItemSeedValidator/Checks/SetRuleCheck.cs:19` (`Run`) implements `ssot-sets.md` §3.4 only — no
  `SetRoleNotUniversal`, no read of `hybridEligible` anywhere in the file — while `ssot-sets.md:288`
  states *"Violation is `SetRoleNotUniversal`, at load"* and `:324` says it fails at import. The gap was
  already noticed in `docs/architecture/item/review/wave2-coverage-gaps.md:192` ("I could not find that
  check actually implemented"). **Cause: the rule is enforced at generation-brief time only
  (`setgen/brief.py:13`, `setgen/roles.py:86`), so nothing mechanical ever re-reads a shipped row.**
  The owning program is `item` (`tasks/item-todo.md`), which is outside this lane's allowed paths, so
  the row is recorded in `tasks/item-seedgen-todo.md` for the manager to route.
- **Precision of the consequence.** A pure humanoid or pure plant wearer *can* still complete these
  sets; the loss is hybrid completability, which `ssot-sets.md` §3.7 makes a guarantee ("Hybrids can
  complete every composable set"). The row's phrasing "a set a player can never finish" is stronger than
  the code supports and is corrected here.
- **`_meta.amendments` is not read by any validator.** The repair writes the file's own provenance
  (`batch`/`model`/`promptVersion`/`authoredUtc`/`sourceRef`/`entries`, the `resocket` precedent), and
  the required `_meta` keys are asserted untouched by a test — but no C# or Python consumer was found
  that validates the amendment shape, so it is documentation-in-data rather than a gated contract.
- **The role re-placement is mechanical, not thematic.** A head slot landing on `girdle`/`mantle`/
  `footing`/`infusion` is a slot-level weight-class choice, not a re-authoring of the item's fiction;
  the sets' names, flavours, notes, atoms and thresholds are untouched by construction and by test.
