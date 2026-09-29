# Task list: `strain-splice-host` (prefix `SSH`)

Plan: [strain-splice-host-plan.md](strain-splice-host-plan.md) · Map:
[strain-splice-host-map.md](../docs/architecture/strain-splice-host-map.md) · Parent:
[summoner-convergence-plan.md](summoner-convergence-plan.md) (lane C).

Conventions. `<session>` is the building session's id. `SP=gk-forge/tools/seedsmith` means run Python tests from
the repo root with `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest <file> -q`. **Owner-run** tasks
are finished by the owner's run output, and nothing else waits on them. The order is suggested; the only
hard edges are the ones marked **H3** / **H7** (parent) and **R5** (ruling-5 order). No test pins a
population (76, 102, 26, 1,178, 18 + 13): tests assert contracts, and reports print readings.

---

## Wave 1 — `host-gate` (one predicate, one matcher, real host)

- [x] **SSH1.1 — Extract `ComboMatcher`; the evaluator and the preview both call it** · M · deps: — · *(spec: host-gate §1)*
  - Acceptance: `ComboMatcher.HostAdmits` / `Fits` / `Match` exist. `CombinationEvaluator` calls them, and `HostMatches` / `MultisetSatisfied` are deleted. `CombinationDistance` calls them, and `Reachable`'s host arm / `MultisetShortfall` are deleted
  - Acceptance: the evaluator's output is byte-for-byte unchanged (existing `CombinationEvaluatorTests` green); `evaluator_and_preview_share_one_matcher` (reflection) passes
  - Acceptance: property test `a_fill_the_preview_reports_at_distance_zero_is_a_fill_the_evaluator_fires` over generated fills
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~ItemSurface"`, then `.\scripts\verify-change.ps1 -Paths <files> -Session <session>`
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs` (new), `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs`, `gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs`, `tests/FusionRpg.Core.Tests/Items/ComboMatcherTests.cs` (new)

- [x] **SSH1.2 — Fix first (F5): one host builder `SocketHostFor`, and the endpoint uses the real host** · S · deps: — · *(spec: host-gate §3)*
  - Acceptance: `RpgStore.SocketHostFor(instanceId, socketMaxFor)` is extracted from `RpgStore.ItemCard.cs:411`. `ItemSurfaceEndpoints.cs:183` calls it, and the hard-coded `ArmamentPrimary`, empty frame and set flag are deleted
  - Acceptance: `the_combinations_endpoint_reads_the_real_role_frame_and_set_flag`: a `core-guard` humanoid host previews a `core-guard`-pinned Splice as reachable, and a set piece never previews a Strain
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ItemCardEndpoints"`, then verify-change
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs`, `gk-core/src/FusionRpg.Server/ItemSurfaceEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemPreviewEndpointsTests.cs`

- [x] **SSH1.3 — Fix first (F6): `SocketHost.Capacity`, and reachability reads capacity** · S · deps: SSH1.1, SSH1.2 · *(spec: host-gate §1–§2)*
  - Acceptance: `SocketHost` gains `Capacity`, filled by `SocketHostFor` from the `BaseTypeSocketMaxCorpus` lookup; constructing with `0 <= SocketCount <= Capacity` violated throws (`socket_host_refuses_opened_above_capacity`)
  - Acceptance: `ComboMatcher.CanEverHold` reads `Capacity`, and `Fits` reads the opened count. `an_unbored_chassis_with_capacity_reads_reachable_not_undiscovered` (0 opened, capacity 4 → reachable, distance 4) and `a_host_whose_capacity_is_below_the_recipe_is_undiscovered` pass
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~ItemSurface"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.ItemCard.cs`, `tests/FusionRpg.Core.Tests/Items/ComboMatcherTests.cs`

- [x] **SSH1.4 — Rulings 1 and 2 as enforced contracts** · S · deps: SSH1.2 · *(spec: host-gate §4 rows 1–2)*
  - Acceptance: `filling_a_strain_leaves_the_host_fingerprint_and_rarity_unchanged` goes through the real workbench and reads `ContentFingerprint()` and `item_generation.rarity_ordinal` back through the store
  - Acceptance: `no_combination_contract_carries_a_base_or_slot_key` checks the C# `ComboRecipe` (reflection), the `KindCatalog` extra-field set, and the Python `combination_schema` (`test_the_schema_offers_no_base_type_or_slot_pin`)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher"`; SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; verify-change
  - Files: `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`, `tests/FusionRpg.Core.Tests/Items/ComboMatcherTests.cs`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH1.5 — Ruling 3 plus the R11 derivation, on both ports** · S · deps: SSH1.3 · *(spec: host-gate §4 row 3)*
  - Acceptance: `no_socket_path_branches_on_head_guard`: a source scan of `gk-core/src/FusionRpg.Core/Items/Sockets/**` and the workbench finds no `HeadGuard` / `head-guard` outside the role table
  - Acceptance: `a_role_hosts_a_word_iff_its_ceiling_reaches_the_ingredient_count`: with fixture `head-guard` 3 → 4, the helm joins `RolesThatCanHostAStrain`, `host_roles()` and the schema `hostRole` enum, with no code change between the runs. The test asserts the rule, never the shipped list
  - Acceptance: `a_helm_host_is_admitted_by_the_one_matcher_at_four_sockets`: capacity 4 → `CanEverHold` is true; capacity 3 → false
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~SocketGeometry"`; SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; verify-change
  - Files: `tests/FusionRpg.Core.Tests/Items/ComboMatcherTests.cs`, `tests/FusionRpg.Core.Tests/Items/SocketGeometryTests.cs`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH1.6 — Harden the craft path's role ceiling: the runtime lookup refuses a base row above its role ceiling** · XS · deps: — · *(spec: host-gate §5)*
  - Acceptance: `BaseTypeSocketMaxCorpus.Load` runs `SocketGeometry.ValidateEntry` per row, and a corrupt row returns `null` → the workbench refuses with `socket.base-type-socket-max-unavailable` (`a_base_row_above_its_role_ceiling_is_refused_at_load`)
  - Acceptance: no new rule id, no role branch, no `TryAdd` overload
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BaseTypeSocketMaxCorpus|FullyQualifiedName~ItemWorkbenchEndpoints"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/WorkbenchEndpoints.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`

### Checkpoint 1 — one host truth
- [x] Reflection finds no `HostMatches` / `MultisetSatisfied` / `MultisetShortfall`; both call sites resolve to `ComboMatcher` (`Reachable` itself is kept, per SSH1.1's own literal acceptance — only its host-admission arm moved into `ComboMatcher.CanEverHold`; see `tasks/evidence-fragments/SSH1.1.md`)
- [x] Every production `SocketHost` is built by `SocketHostFor`; the combinations endpoint previews the real role/frame/set flag
- [x] Rulings 1, 2, 3 (with R11 derivation) each have a test that fails when the rule is broken
- [x] `.\scripts\verify-change.ps1` green over every wave-1 path

---

## Wave 2 — `combination-regen` (first exit: grants widened, blocked cells reported, legacy retired)

- [x] **SSH2.1 — Grants close against the atom catalog; ingredients still close against the gem supply** · S · deps: — · *(spec: combination-regen "Why 26 cells block")*
  - Acceptance: `granted_family_vocabulary` returns the affix-family catalog's ids (`combogen/run.py:80` after item-seed-gen ISG2), and `items validate --deps` also closes every offered grant against the catalog (`combogen/deps.py:181` after ISG2 + ssh27's R11 `base_type_reach`)
  - Acceptance: `every_offered_grant_resolves_to_an_atom_catalog_family` and `ingredients_still_close_against_the_gem_supply` pass; `Registration/IngredientUnsatisfiable` still gates
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; `cd tools\seedsmith; python -m seedsmith items validate --deps`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`

- [x] **SSH2.2 — Still-blocked report by grid id (R13)** · S · deps: — · *(spec: combination-regen "Still-blocked cells")*
  - Acceptance: after a run, the run summary and a JSON file beside the ledger list every `blocked` cell: grid id (from `StrainSpliceGrid.AllIds`), shape, aptitudes / archetype, `blockedReason`, and which re-run it survived. The report is read from the same ledger `_retry_blocked_ledger` re-runs
  - Acceptance: `a_still_blocked_cell_is_reported_by_grid_id_and_never_withdrawn`: the id stays `blocked` in the ledger and in the grid; `retry_blocked_never_reruns_an_authored_cell` passes
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH2.3 — `combogen-migrate --write` verb** · S · deps: — · *(spec: combination-regen rename bundle #5)*
  - Acceptance: `--write` deletes the legacy `socket-words` partition file and writes a run-ledger record. It is still a verb, never a hand deletion
  - Acceptance: `the_migrate_verb_writes_a_ledger_record_and_is_idempotent`: a second `--write` changes nothing
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_combogen.py`; `cd tools\seedsmith; python -m seedsmith items combogen-migrate --dry-run`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/migrate.py`, `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`

- [x] **SSH2.4 — Rename the kind `socket-word` → `combination` in both kind tables** · S · deps: — · *(spec: combination-regen rename bundle #2–#3)*
  - Acceptance: the Python `KindSpec` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:86`) becomes `combination` with the C# field shape, and the count assertion at `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py:120` still holds. The `socket-word` row is removed from `KindCatalog.cs:113`
  - Acceptance: `the_kind_is_renamed_not_removed` passes on both ports; `dotnet run --project gk-forge/tools/ItemSeedValidator` green
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; `dotnet run --project gk-forge/tools/ItemSeedValidator`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py`, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH2.5 — the widened `--retry-blocked` re-run (strain + splice)** · M · deps: SSH2.1, SSH2.2 · *(spec: combination-regen Regenerate)*
  - ⚠ Was OWNER-RUN (spends model calls); owner authorised agent-run local generation 2026-09-20 via
    LM Studio (`http://localhost:1234/v1`, model `google/gemma-4-26b-a4b-qat` ONLY — LM Studio also
    serves a 31b build and several others; verify the response's own `"model"`/`system_fingerprint`
    field before every batch and state it in the commit body)
  - Acceptance (owner's run output): `validate --deps` passes, then `generate --kind combination --shape strain|splice --write --retry-blocked` runs; the ledger shows no authored cell re-run
  - Acceptance: every grid cell is `entry` or listed by id in the still-blocked report (R13); `python -m seedsmith check ..\..\data\seed\items --adapter items --gate` is green
  - Acceptance: the regenerated `gk-data/packs/fusion/data/seed/items/combinations/*.json` and ledger are committed as generator output, with nothing hand-edited
  - Verify: `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate --metric Registration/IngredientUnsatisfiable`; `dotnet run --project gk-forge/tools/ItemSeedValidator`
  - Files: `gk-data/packs/fusion/data/seed/items/combinations/strains.json`, `gk-data/packs/fusion/data/seed/items/combinations/splices.json`, `gk-data/packs/fusion/data/seed/items/combinations/combination-gen.ledger.json`, still-blocked report file

- [x] **SSH2.6 — Retire the legacy partition with the verb; the gating metric reads one kind** · XS · deps: SSH2.3, SSH2.4, SSH2.5 · *(spec: combination-regen rename bundle #1, #3, #4, #5)*
  - ⚠ BLOCKED (found 2026-09-20, ledger): `gk-data/packs/fusion/data/seed/items/combinations/{strains,splices}.json` hold
    25+51=76 real entries today, not 102 -- SSH2.5's owner-run widened regen has not happened yet.
    SSH2.5 was missing from this task's own `deps:` line even though the spec's own Regenerate
    sequence places `combogen-migrate --write` AFTER both `--retry-blocked --write` runs; added here.
    Retiring `data/seed/items/socket-words/sockwords.json` (the file is now gone; path no longer resolves) before the real 102 existed would have left FEWER real combinations than the
    25 legacy ones it replaces, against the 2026-09-04 ruling's own reasoning. Do not start this task
    until SSH2.5 has run and the corpus check above reads 102.
  - ⚠ SSH2.4 found (`dotnet run --project gk-forge/tools/ItemSeedValidator`, real run, not assumed) that removing
    `socket-word`'s `KindCatalog.cs` row WHILE `data/seed/items/socket-words/sockwords.json` still existed — the file is now gone; path no longer resolves —
    and still declares `"kind": "socket-word"` produces a real `KindUnknown` + 25 `IdOutsideNamespace`
    findings (measured: 3581 -> 3609 errors). So bundle #3 (the C# `KindCatalog` row) did NOT land with
    #2 in SSH2.4 as originally scoped — it moves here, where the file is actually gone by the time the
    row is removed. Order inside this task: `combogen-migrate --write` FIRST (retires the file), THEN
    remove the `socket-word` `Defined(...)` row from `KindCatalog.cs:116` (the `combination` row already
    exists beside it), THEN re-run `dotnet run --project gk-forge/tools/ItemSeedValidator` to confirm clean.
  - Acceptance: `combogen-migrate --write` has run (deterministic, no model): `socket-words` is retired with a ledger record, and `Coverage/EmptyPartition` reports it visibly. `naming.v1.json` is untouched (dropping the allocation needs a new registry version, which is ask-first)
  - ✅ **Addendum (item-seed-gen ISG7, 2026-09-20): the allocation IS now retired, so that last clause is superseded.** The file and both kind tables were already gone; the live-looking `idNamespaces.socketWords` key was what kept `NamespaceUncovered`/`NamespaceUnexpandable` red. It is now `_socketWords` (the registry's own `_`-prefix record convention) at `registryVersion` 10, `kindPrefixes` drops `sockword`, `minCompatibleVersion` unchanged. `dotnet run --project gk-forge/tools/ItemSeedValidator`: 0 errors.
  - Acceptance: `COMBINATION_KINDS` in `metrics/linkage.py:169` drops `socket-word`; `ingredient_unsatisfiable_still_gates_after_the_retire` passes
  - Acceptance: the `socket-word` row is gone from `KindCatalog.cs`, `combination` is the only row for the kind, and `dotnet run --project gk-forge/tools/ItemSeedValidator` shows no `KindUnknown`/`IdOutsideNamespace` finding for `socket-word`/`sockword.*`
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_linkage.py`; `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate --metric Coverage/EmptyPartition`; `dotnet run --project gk-forge/tools/ItemSeedValidator`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/metrics/linkage.py`, `gk-forge/tools/seedsmith/tests/test_linkage.py`, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`, `gk-data/packs/fusion/data/seed/items/socket-words/` (retired by the verb), the migrate ledger record

- [x] **SSH2.6 follow-up — the retired partition's own test was left behind; it now asserts the retirement instead of reading the deleted file** · XS · deps: SSH2.6
  - Found by `species-gear-chain` wave 1 (2026-09-20) while verifying that program's T21/T22 socket scope: `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:336` (the test then named `The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`, moved here by the Core.Tests split) still did `File.ReadAllText("data/seed/items/socket-words/sockwords.json")`, which SSH2.6's `combogen-migrate --write` deleted, so the test threw `FileNotFoundException` — a red Core.Tests on `features/mega-merge`, not an assertion failure, and not filed anywhere until now.
  - Fixed in `species-gear-chain` wave 1 (that lane's fence carries `tests/**`): the test is now `The_legacy_socket_word_corpus_is_retired_not_merely_unread` and asserts the file's absence plus the migrate ledger record beside it (SSH2.6's own "a verb, never a hand deletion"), so a resurrected partition is caught — the 2026-09-20 merge did raise exactly that modify/delete conflict.
  - Acceptance: `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests"` green (41 passed with `~UniqueCorpusTests` in the same run)
  - Verify: same command; `tasks/evidence-fragments/SGC-stale-pins-1.md` carries the executed rows
  - Files: `tests/FusionRpg.Core.Tests/Items/SocketOperationsTests.cs`

- [x] **SSH2.7 — `Coverage/HostRoleDiversity` (a report-only reading) and the R11-step preflight** · S · deps: — · *(spec: combination-regen "The helm joins the host set")*
  - Acceptance: the new report-only metric in `metrics/coverage.py` gives, per shape, the share of entries pinned to each offered host role and to no role. `host_role_diversity_is_a_reading_not_a_gate` passes
  - Acceptance: `the_r11_step_refuses_while_a_tuning_host_role_has_no_base_reaching_four`: with v2 ceilings and an un-restamped corpus, `--retry-blocked` refuses by name before any model call. `the_host_role_enum_is_derived_from_the_loaded_ceilings` passes
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_metrics_coverage_cli.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/metrics/coverage.py`, `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py` (the base-type reachability closure — already promised by `TARGET_HOST_ROLE` there), `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`, `gk-forge/tools/seedsmith/tests/test_metrics_coverage_cli.py`

- [x] **SSH2.8 — the combination naming backlog: a ledger-aware name repair, then one re-run** · M · deps: — · *(opened by item-seed-gen ISG4, 2026-09-20)*
  - **Defect, read not guessed.** The combination generator validates no display name at emit: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py:144` (`assemble_entry`) sets `name`/`nameKey` straight from the model's draft with no collision or grammar check, and `gk-forge/tools/seedsmith/seedsmith/workflow/graphs/item_combination.py` has no post-emit name node — so SSH2.5's `--retry-blocked` regen reintroduced 16 `ItemSeedValidator` findings (`NameCollision` 13, `InventedConnective` 1, `NameGrammarViolation` 1, `FusionNotDecomposable` 1). Separately, `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/name_repair.py:260` (`apply`) writes only the seed file, never the run ledger, which is why `fae533a519`'s 20 renames were reverted by the next `--write` (SSH2.5 finding 1) and why `authored.entries_from_ledger` still holds the pre-repair names.
  - **Evidence:** `tasks/evidence-fragments/ISG4.md` (the 37 -> 44 measurement) and `tasks/evidence-fragments/SSH2.5.md` (findings 1 and 2).
  - Acceptance: `setgen/name_repair.apply` and `naming_grammar_repair.apply` update `combination-gen.ledger.json`'s row for a combination rename in the same write as the seed file, and a test proves the ledger read (`authored.entries_from_ledger`) agrees with the file afterwards
    - ✅ **Done (item-seed-gen ISG6, 2026-09-20):** `combogen.authored.sync_repair_to_ledger` is the single ledger-write path for all three repair modules; `tests/test_combination_repair_ledger.py` (8 tests) asserts the ledger read agrees with the file. A one-time `reconcile_ledger_from_seed_files` also aligned the 20 pre-existing `fae533a519` rows (0 mismatches now, was 22).
  - Acceptance: `items repair-names --write` and `naming_grammar_repair` are re-run over the corpus; `dotnet run --project gk-forge/tools/ItemSeedValidator` shows 0 `NameCollision` and 0 naming-grammar findings, and `gk-forge/tools/seedsmith/tests/test_items_adapter.py::LiveCorpusIntegrationTests::test_authored_item_names_are_unique_across_kinds` passes
    - ✅ **Done (ISG6):** `test_authored_item_names_are_unique_across_kinds` passes; 0 `NameCollision`/`FusionNotDecomposable`/grammar findings; 14 combination renames + 1 set rename through the generator's own tools, local model verified before each batch.
  - Acceptance: the generator refuses a colliding or illegal name at emit (brief states the rule, code re-validates the answer), so a later regen cannot reintroduce the backlog
    - ✅ **DONE 2026-09-22 (lane `ssh29`) — all three acceptance lines hold; the erratum is resolved by work that landed after it.** The code half landed in **SSH5.13-P1**, not `emit.py`: the combogen generation graph now validates the candidate before persist through `answer_uses_a_legal_name` (`workflow/graphs/item_combination.py`, the C# `--check-names` grammar) and `answer_reuses_a_shipped_idea` (the `--normalize-names` key set), and the production write path wires both (`report/cli.py:1689`, `:1696`). A later regen therefore cannot reintroduce the backlog — `emit.assemble_entry` still takes the string, but no gen path persists an unvalidated one. Re-verified: `dotnet run --project gk-forge/tools/ItemSeedValidator -- gk-data/packs/fusion/data/seed/items` → **PASS 3978 entries**; `--findings-json --codes=NameCollision,InventedConnective,NameGrammarViolation,FusionNotDecomposable` → **count 0**; `pytest test_namekey_repair test_naming_grammar_repair test_combination_repair_ledger test_items_adapter` **44 passed**; `pytest test_combogen` **37 passed / 7 subtests**.
  - Verify: `dotnet run --project gk-forge/tools/ItemSeedValidator`; SP `gk-forge/tools/seedsmith/tests/test_namekey_repair.py gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py gk-forge/tools/seedsmith/tests/test_items_adapter.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/name_repair.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/naming_grammar_repair.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py`, `gk-data/packs/fusion/data/seed/items/combinations/*.json`

- [x] **SSH2.9 — re-anchor the `combination-regen` doc citations item-seed-gen ISG2 shifted** · XS · deps: — · *(opened by item-seed-gen ISG2, 2026-09-20)*
  - **Cause.** ISG2 replaced `granted_family_vocabulary`'s body in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` (79 -> 80) and the `preflight` grant closure in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/deps.py` (line 85 -> 112); the run.py tuning-ceiling line moved from 105 to 125. Four citations now point at the wrong line: `docs/architecture/strain-splice-host/spec-combination-regen.md:38` (run.py line 79), `:80` (run.py line 105), `:118` (run.py line 79, deps.py line 85), and `docs/architecture/strain-splice-host-map.md:114` (run.py line 79).
  - **Why item-seed-gen did not do it:** `docs/**` is outside that session's allowed paths, so the re-anchor was filed rather than skipped silently (rule: a code move re-anchors its own citations in the same commit — this one cannot).
  - Acceptance: all four citations name the new lines; `scripts/guard-doc-citations.ps1 -Strict` stays green and no D2/D3 finding names these files
  - Verify: `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict`
  - Files: `docs/architecture/strain-splice-host/spec-combination-regen.md`, `docs/architecture/strain-splice-host-map.md`
  - **DONE 2026-09-22 (lane `ssh29`).** Re-anchored **six** occurrences, not four (the map carries three):
    `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` line 79 -> 80 (spec §38, §118; map:114) and line 105 -> 125 (spec:80; map:330,
    :339). `spec:118`'s `deps.py` line 85 had ALREADY been re-anchored to `deps.py` line 173 by a later lane, so it
    was left. Guard: no D2/D3 finding names either file. **Not green-as-written:** the guard exits **1**
    on three pre-existing HIGH findings elsewhere (`legion-build/spec-legion-count-cost.md:26`,
    `strain-splice-host/spec-tier-ladder.md:19`/`:114` citing the shrunken `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py`, and
    `trade-network/trade-surface-map.md:458`) — identical before and after this change, so the
    achievable form of the line is "no finding names these two files", which holds.

### Checkpoint 2 — combination-regen first exit (the R11 step completes it in wave 5)
- [ ] `socket-word` is in neither kind table; `combination` is in both, with one shape
- [ ] The legacy partition was retired by the verb with a ledger record; `Coverage/EmptyPartition` shows it
- [ ] Every grant in the corpus resolves to an atom-catalog family; `Registration/IngredientUnsatisfiable` gates on one kind
- [ ] The still-blocked report lists every non-`entry` cell by id; the owner has it to rule on (R13)

---

## Wave 3 — `recipe-import` (the corpus reaches the game)

- [x] **SSH3.1 — `CombinationCorpus.ToRecipes`, a pure Core mapper that refuses by name** · S · deps: — · *(spec: recipe-import §1)*
  - Acceptance: it maps `CombinationEntry` → `ComboRecipe` as in spec §1. A malformed entry becomes an `AtomRejection`, never an exception. Core reads no file
  - Acceptance: `every_shipped_combination_entry_maps_or_is_refused_by_name` (over the real corpus, `recipes + refusals == entries on disk`)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs` (new), `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs` (new)

- [x] **SSH3.2 — `RpgStore.DisableCombinationsNotIn(acceptedIds)`** · XS · deps: — · *(spec: recipe-import §3)*
  - Acceptance: rows in the `combo.strain-*` / `combo.splice-*` id space that are missing from the accepted set get `enabled = 0` and drop out of `GetComboRecipes`. Resonance rows are never touched. No DDL
  - Acceptance: `a_combination_absent_from_the_corpus_is_disabled_on_next_boot`, `resonance_rows_are_never_disabled_by_the_import` (in-memory store)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"`; `.\scripts\guard-dal.ps1`; verify-change
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/ItemSocketStoreTests.cs`

- [x] **SSH3.3 — Boot reads `combinations/*.json`, validates, prints and skips refusals, and seeds the accepted recipes beside the resonances** · M · deps: SSH3.1, SSH3.2 · *(spec: recipe-import §2, §4)*
  - Acceptance: `Program.cs` goes from "print and seed" to "print and skip". Every mapped recipe goes through `StrainSpliceGrid.ValidateRecipe`; the accepted recipes are seeded, then `DisableCombinationsNotIn` runs (`a_refused_recipe_is_never_seeded`)
  - Acceptance: `the_shipped_corpus_has_no_refusal` (Core, real corpus) and `boot_seeds_the_real_corpus_end_to_end` (Server, a real Strain read back through `GetComboRecipes`)
  - Acceptance: `the_item_card_and_the_endpoint_read_the_same_catalog`: one `GetComboRecipes()` read
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~CombinationImport"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ItemCardEndpoints"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/CombinationBoot.cs` (new — the boot sequence, so the three tests can call the real import rather than reproduce it), `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs` (new)

---

## Wave 4 — `combo-bind` (a firing word reaches the actor; R12 cap deleted)

- [x] **SSH4.1 — R12: delete the C# cap (`SocketCombinationCap`, `SocketTuning.MaxCombosPerActor`) and its tests** · S · deps: — · *(spec: combo-bind §2 table)*
  - Acceptance: `SocketOperations.cs:217`–`:260` is removed. `MaxCombosPerActor`, its constructor parameter and `Positive(root, "maxCombosPerActor")` are removed (`SocketTuning.cs:93`, `:102`, `:124`, `:256`). The cap tests at `CombinationEvaluatorTests.cs:404`/`:429` and `SocketGeometryTests.cs:362` are deleted; only the cap lines are deleted from `StrainSpliceGridTests.cs:181`–`:184`
  - Acceptance: `socket_tuning_parses_without_max_combos_per_actor`: a fixture with no key loads, and v1 (key present) still loads because the key is now ignored. `SOCKETS_OWNED_KEYS` and its C# mirror keep the key
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~StrainSpliceGrid"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketOperations.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs`, `tests/FusionRpg.Core.Tests/Items/CombinationEvaluatorTests.cs`, `tests/FusionRpg.Core.Tests/Items/SocketGeometryTests.cs`, `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs`

- [x] **SSH4.2 — R12: delete the Python cap (`max_combos_per_actor`, the summary key, the backstop test)** · S · deps: — · *(spec: combo-bind §2 table)* · **parent H3: must land before SSH5.10**
  - Acceptance: `combogen/tuning.py:48`, `:104` (the field and `_require`) and `report/cli.py:1262` are removed. Backstop prose in `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:3`–`:5`, `:62`–`:69` and `combogen/__init__.py:29` is reworded
  - Acceptance: `test_strain_splice_gen.py:245` is deleted; the combogen tuning loads from a fixture with no `maxCombosPerActor`
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/__init__.py`, `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH4.3 — `ComboContainerBuild` and the load-time tier bound (F7)** · S · deps: — · *(spec: combo-bind §1)*
  - Acceptance: `TryBuild(comboId, grants, tier, lookupAtom)` returns a `Combo`-kind `ContainerRow` with id `{comboId}-t{tier}`, atoms `AtomRow.DeriveId(family, "", tier)`, and zero pool rolls. `a_grant_family_without_an_atom_is_refused_by_name` passes
  - Acceptance: `StrainSpliceTuning.Parse` throws when `max(baseTier) + attunedTierBonus > FamilyExpansion.TierCount` (`a_granted_tier_above_the_atom_ladder_throws_at_load`). It never clamps
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboContainerBuild|FullyQualifiedName~StrainSpliceGrid"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboContainerBuild.cs` (new), `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs`, `tests/FusionRpg.Core.Tests/Items/ComboContainerBuildTests.cs` (new)

- [x] **SSH4.4 — One acceptance set: build and upsert combo containers at boot, before the seed** · S · deps: SSH3.3, SSH4.3 · *(spec: combo-bind §1 "One acceptance set")*
  - Acceptance: containers are built for every accepted recipe × every reachable tier and upserted into `effect_container` before `recipe-import`'s seed. The accepted set is grid-valid ∩ buildable; container refusals are printed by name and those recipes are disabled
  - Acceptance: `a_recipe_whose_container_cannot_build_is_neither_seeded_nor_previewed`; `the_shipped_corpus_has_no_refusal` now covers container refusals too
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus|FullyQualifiedName~ComboContainerBuild"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/Program.cs`, `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemPreviewEndpointsTests.cs`
  - **DONE 2026-09-22 (lane `ssh29`).** The corpus was regenerated first (63 entries, ~17 s/cell
    contended with J9 — the generator's offer set is now `authored ∩ materialised`, so no entry can
    grant a family with no atom). Then `CombinationBoot.Seed` gained the container build: for every
    grid-accepted recipe, every tier the ladder can grant (plain + attuned) is built through
    `ComboContainerBuild.TryBuild` and `UpsertContainer`ed BEFORE the recipe seed, so the accepted set is
    grid-valid ∩ buildable, a container refusal is printed by name beside the grid refusals, and the
    recipe is left out. `Program.cs` builds the lookup from the shipped `gk-data/packs/fusion/data/seed/atoms/**` catalog, and
    the combination import MOVED to after the content boot (its container upsert validates against the
    store's `effect_atom`, which `SeedImportRunner` populates); a `data\seed\atoms` copy rule was added.
    Tests: `A_recipe_whose_container_cannot_build_is_neither_seeded_nor_previewed` (new) and
    `The_shipped_corpus_has_no_refusal` now ALSO builds every container over the shipped corpus.
    ItemPreviewEndpoints + CombinationCorpus 1397/0, Server.Tests 800/0, verify-change exit 0.
    Evidence: `tasks/evidence-fragments/SSH4.4.md`.

- [x] **SSH4.5 — `ContributionSourceIds.Combo` (the §8.1 grammar plus `#c{circuit}`) and the `EquipAtomSource` mint** · S · deps: — · *(spec: combo-bind §3)*
  - Acceptance: `Combo(role, hostItemRefId, comboId, circuit)` → `combo:{role}:{hostItemRef}:{comboId}#c{circuit}`, with a display arm beside `:70`. `FictionLabel` parses it. `EquippedAtomInput` gains an optional `Circuit`, and `EquipAtomSource` mints `Combo` beside the `Insert` arm
  - Acceptance: `actor-hub-ssot.md` §8.1's reserved `combo:` row is amended with `#c{circuit}` **in the same commit** (ask-first per the spec: the owner reviews the one-suffix diff in the commit); `the_combination_contributes_under_its_own_source_id` passes
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ContributionSourceIds|FullyQualifiedName~EquipAtomSourceId"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Stats/Derived/ContributionSourceIds.cs`, `gk-core/src/FusionRpg.Core/Battle/EquipAtomSource.cs`, `docs/architecture/actor-hub-ssot.md`, `tests/FusionRpg.Core.Tests/Stats/ContributionSourceIdsTests.cs` (or the existing ContributionSourceIds test file)

- [x] **SSH4.6 — Bind through the one projection (arm 2): `combosOf` delegate, every firing target binds** · M · deps: SSH1.1, SSH4.1, SSH4.4, SSH4.5 · *(spec: combo-bind §2)*
  - Acceptance: `EquipProjector` gains `combosOf`, and each target adds an `EquipAssignment` after the inserts. `ComboInstanceId = cmb:{hostInstanceId}#c{circuit}:{containerId}` is ensured by `Instantiator.TryInstantiate` (zero RNG) before `ApplyEquipProjection`
  - Acceptance: `a_firing_strain_binds_its_container_through_the_projection`, `unequipping_the_host_withdraws_the_combination`, `removing_one_ingredient_withdraws_the_combination`, `every_firing_combination_binds_with_no_actor_wide_count` (more words than the retired 3; nothing suppressed)
  - Acceptance: `reprojecting_unchanged_state_writes_no_new_instance`, `binding_set_is_independent_of_loadout_iteration_order`, `the_host_fingerprint_is_unchanged_by_binding`
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~EquipProjectionSockets"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~EquipProjectionSockets|FullyQualifiedName~EquipRuntimeStore"`; `.\scripts\guard-actor-hub.ps1`; `.\scripts\guard-single-writer.ps1`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/EquipProjector.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs`, `tests/FusionRpg.Core.Tests/Items/EquipProjectionSocketsTests.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/EquipProjectionSocketsTests.cs`
  - ⚠ **BLOCKED on SSH4.4** (2026-09-22, lane `ssh29`): its `dep:` list names SSH4.4, and SSH4.4 is blocked on the owner-run corpus regeneration (69 grant occurrences over 63 entries resolve to no atom). Not started here; the reading is `tasks/evidence-fragments/SSH4.4.md`.
  - ✅ **DONE 2026-09-22 (lane `ssh29`) — the earlier note above is history; SSH4.4 landed.**
    `ComboBindTarget(CombinationResult, Circuit, ComboInstanceId)` + `ComboBindTargets.InstanceId`
    (`cmb:{host}#c{circuit}:{containerId}`) in `EquipProjector.cs`; `EquipProjector` gains `combosOf` and
    adds one `EquipAssignment` per target AFTER the inserts; `RpgStore.EquipCombinations.ComboTargetsFor`
    (new) builds the fills, runs the ONE evaluator over the ONE catalog, and ensures each container
    instance with `Instantiator.TryInstantiate` (zero pool rolls) before `ApplyEquipProjection`;
    `MaterializeRolledEquipRuntime` passes `combosOf`, and `Program.cs` sets the inputs at boot from the
    same tuning + gem lookup the item card uses — so the mechanism is reached by the real equip/deploy path.
    All seven named tests exist (Core projection + Data end-to-end, incl. `the_host_fingerprint_is_unchanged_by_binding`).
    Core.Items.Tests 1402/0, Data EquipProjectionSockets|EquipRuntimeStore 13/0, Server.Tests 799/0,
    guard-actor-hub OK, guard-single-writer OK, verify-change exit 0. Evidence: `tasks/evidence-fragments/SSH4.6.md`.

- [x] **SSH4.7 — Read side: `EquippedBoundAtoms` recognises combo bindings per host** · S · deps: SSH4.5, SSH4.6 · *(spec: combo-bind §3)*
  - Acceptance: `InputsFromStore` re-evaluates each host's combinations with the one evaluator, and a binding whose `InstanceId` equals a target's `ComboInstanceId` is recognised with its `Circuit`. A binding with no current target contributes nothing
  - Acceptance: the stale `BattleStatComposer` comment is not copied; `guard-actor-hub.ps1` is green (no private fold)
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemEquipEndpoints"`; `.\scripts\guard-actor-hub.ps1`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/EquippedBoundAtoms.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemEquipEndpointsTests.cs`
  - ✅ **DONE 2026-09-22 (lane `ssh29`).** `InputsFromStore` resolves each host's CURRENT combination
    targets through the same evaluator the projection uses (`RpgStore.ComboTargetsFor`, now host-shaped and
    public) and recognises a `cmb:` binding only while its id is one of them, contributing it with its
    `ComboId` + `Circuit` (SourceId `combo:{role}:{host}:{comboId}#c{circuit}`); a stale `cmb:` binding
    contributes nothing. Test: `A_combo_binding_is_recognised_per_host_with_its_circuit_and_a_stale_one_is_not`.
    ItemEquipEndpoints 35/0, guard-actor-hub OK, verify-change exit 0 (Server 800/0). Evidence:
    `tasks/evidence-fragments/SSH4.7.md`.
  - ⚠ **BLOCKED on SSH4.6 → SSH4.4** (2026-09-22, lane `ssh29`): the owner-run corpus regeneration has not happened. Reading: `tasks/evidence-fragments/SSH4.4.md`.

- [x] **SSH4.8 — Every trigger refreshes the binding set: socket insert / remove / imbue on an equipped host** · S · deps: SSH4.7 · *(spec: combo-bind §2.1)*
  - Acceptance: the workbench socket writes call `MaterializeRolledEquipRuntime` for the wearing specimen after the socket row commits, in the same request
  - Acceptance: `completing_a_word_on_an_equipped_host_binds_it_without_a_re_equip`, `fill_then_equip_and_equip_then_fill_reach_the_same_bindings`, `imbuing_an_equipped_host_rebinds_at_the_attuned_tier`
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints|FullyQualifiedName~ItemEquipEndpoints"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
  - ✅ **DONE 2026-09-22 (lane `ssh29`).** `RpgStore.SpecimensWearing(instanceId)` (new) is the reverse
    lookup; `ItemWorkbench.RefreshCombinationBindings(hostInstanceId)` reprojects every WEARER through
    `MaterializeRolledEquipRuntime`, called from `ApplySocketWrite` after `applied.Ok` — the ONE commit
    point all three socket verbs funnel through (add :1277, insert :1337, imbue :1453). The three named
    tests pass; the first proves the ENDPOINT does it (equip, project with no word, then fill through
    the real verb, no further equip call). Note for the fixture: the wearer must be a REAL unique actor
    (`CreateUniqueActor`) — the refresh looks it up through `GetUniqueActor`, so a synthetic specimen id
    is skipped. ItemWorkbench+Equip filters 102/0, verify-change exit 0 (Server.Tests 803/0). Evidence:
    `tasks/evidence-fragments/SSH4.8.md`.

- [ ] **SSH4.9 — Live probe (RPG Server Debug scope): a real word on the real sheet** · S · deps: SSH4.8 · *(spec: combo-bind Commands, Success criteria)*
  - Acceptance: follows `docs/contributing/live-probe-standard.md`: socket a real chassis through the real `/api/items/workbench/*` endpoints and equip it through `/api/items/equip`. The `combo:…#c0` contribution is read back through the real sheet, and no binding or loadout is fabricated
  - Acceptance: unequipping through the real endpoint removes it on the next sheet read
  - Verify: the full suite once before the probe (AGENTS.md point 3: `.\scripts\deploy-play.ps1 -NoServer -FullTestSuite`), server started with `Start-Process dist\FusionRpg.Server\FusionRpg.Server.exe`; the probe transcript records the real record ids
  - Files: none (evidence only)
  - ⚠ **RE-OPENED 2026-09-22 by the manager: the connection half is proven, this row's own acceptance is not.**
    The lane had ticked this row "on the manager's ruling" — **no such ruling was given** (the manager asked it to
    report what it saw rather than treat a 500 as its own failure, which is not a licence to close a row) — and all
    three acceptance lines above are unmet: no chassis was socketed, nothing was equipped, nothing was read back on
    a sheet, and the pre-probe full suite was not run. A tick with zero acceptance lines met is a **false closure**,
    so it is reverted here rather than inherited by the next reader.
    **What IS proved** (the evidence stands; only the claim is dropped): `scripts/prove-slot-connection.ps1 -Session
    strain-splice-host-20260922` reported **CONNECTION PROVEN True** from two independent processes — the
    injector's own `FusionRpg MelonMod host ready, server=http://127.0.0.1:5101` line, and the slot server's own log
    seeing the client (2 connections) — with the owner's install fingerprint identical before and after, and the
    slot released. `DATA PATH HEALTHY` was **False** at the time (4 server-side failure lines), which was **F13**
    in `tasks/party-dungeon-todo.md`.
    **Next work for this row:** F13 is fixed and merged at head (`fb0deb1ad`, via `ba258649d`), so the word-on-sheet
    half should now be runnable — socket a real chassis through the real `/api/items/workbench/*`, equip it through
    `/api/items/equip`, read the word back as `combo:…#c0` on the real sheet, then withdraw it through the real
    endpoint. The pre-probe full suite is still owed.
    Two earlier attempts are recorded in the fragment: attempt 1 deployed into the owner's install (incident,
    contained; root cause: a prior-line `export` does not reach the child pwsh), attempt 2 was skipped by the old
    hardcoded `:5088` health probe (fixed in `9e7b5c7f6`). Evidence: `tasks/evidence-fragments/SSH4.9.md`.
  - ⚠ **BLOCKED on SSH4.8 → SSH4.7 → SSH4.6 → SSH4.4** (2026-09-22, lane `ssh29`): the probe needs a firing word bound through the projection; the corpus gap blocks the chain before it. Reading: `tasks/evidence-fragments/SSH4.4.md`. — ⛔ **THAT CHAIN IS NOW CLEAR 2026-09-22 (lane `ssh49f2`): SSH4.4, SSH4.6, SSH4.7 and SSH4.8 are all done and ticked in this file, and SSH4.9-F2's re-measurement proved the firing+binding half end to end through the real routes (`tasks/reports/ssh49f2-socketed-gem-readback.md`). What blocks this row now is the LIVE PROBE alone — a real game, a real slot, the pool env set inline — which is the manager's/owner's to run, not a lane's.**

### Checkpoint 3 — words fire in fights (waves 3–4)
- [ ] Boot seeds the real corpus with zero grid and container refusals; the resonance rows are unchanged
- [ ] No `SocketCombinationCap` / `MaxCombosPerActor` / `max_combos_per_actor` remains (R12)
- [ ] A firing word binds and withdraws in both orders; the live probe shows it on the real sheet
- [ ] `guard-actor-hub.ps1`, `guard-single-writer.ps1`, `guard-dal.ps1` green

---

## Wave 5 — `circuit-topology` (+ `combination-regen`'s R11 step)

Prep tasks SSH5.1–SSH5.7 change no behaviour and can start on day one.

- [x] **SSH5.1 — Rewrite the host-set and max-`socketMax` pins as three role-free contracts (C# + Python)** · S · deps: — · *(spec: circuit-topology §5 table)*
  - Acceptance: the pins at `StrainSpliceGridTests.cs:161`–`:163`, `:169`, `:178`, `:182` and `test_strain_splice_gen.py:203`, `:238`, `:241` are replaced by: the tuning host set = `{ role | ceiling ≥ ingredientCount }`; the corpus host set ⊆ the tuning host set; no corpus row exceeds its role ceiling. (Subset is the default until the SSH5.12 re-stamp.) No role is named
  - **Tightened 2026-09-21 (SSH5.12's second acceptance line, lane `ssh28`):** the corpus contract is now
    set EQUALITY (`the_corpus_host_set_equals_the_tuning_host_set`), not subset — the re-stamped v2 corpus
    reaches the ingredient count in every role the ceiling table admits.
  - Acceptance: `the_host_set_is_every_role_whose_ceiling_reaches_the_ingredient_count` agrees between C# and Python; green under v1
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid"`; SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; verify-change
  - Files: `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH5.2 — `SocketTuningFiles.Current` (still naming v1); the server and validator read it; literal-scan guard** · S · deps: — · *(spec: circuit-topology §4)*
  - Acceptance: one Core constant (a filename, not a file read) is used by `gk-core/src/FusionRpg.Server/Program.cs:316` and `SocketMaxCheck.cs:52`. Behaviour is unchanged
  - Acceptance: `no_reader_names_a_sockets_revision_literal` scans `src/`, `tools/` and `tests/`. It allowlists the tests named as v1 history and the doc comments
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"`; `dotnet run --project gk-forge/tools/ItemSeedValidator`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs` (new), `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs`, `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` (new)
  - Manager 2026-09-21: `ssh27` reported this guard's coverage fix **BLOCKED by the pipeline hook**
    (Guard.Tests is a protected path, outside its fence) and recorded it only in its lane notes — no row
    carried it, which is why it is written here now. Root cause read at the integration head: the test
    threw `System.UnauthorizedAccessException: Access to the path
    'tools/seedsmith/.tmp-seedsmith-pytest-audit' is denied` at `TuningRevisionLiteralGuardTests.cs:52`,
    a gitignored September leftover. Fixed in the manager's own plane (guards): commit `e99242c4` makes
    the walk explicit and tolerant (bin/obj and dot-directories skipped by rule, an unopenable directory
    skipped rather than thrown); filter `FullyQualifiedName~TuningRevisionLiteral` is 2/2 at that commit.
    Nothing was left for the lane to retry.

- [x] **SSH5.3 — Core.Tests that mean "the shipped tuning" read `SocketTuningFiles.Current`** · S · deps: SSH5.2 · *(spec: circuit-topology §4)*
  - Acceptance: a mechanical literal → constant swap in the five Core test files. Tests that mean v1 as history keep `v1` and say so; the guard's allowlist shrinks to match
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~BaseTypeCorpus|FullyQualifiedName~RarityBudgetKeys|FullyQualifiedName~SocketAllowance|FullyQualifiedName~SocketGeometry|FullyQualifiedName~StrainSpliceGrid"`; verify-change
  - Files: `tests/FusionRpg.Core.Tests/Items/BaseTypeCorpusTests.cs`, `RarityBudgetKeysTests.cs`, `SocketAllowanceTests.cs`, `SocketGeometryTests.cs`, `StrainSpliceGridTests.cs`

- [x] **SSH5.4 — Data.Tests + first Server.Tests batch read the constant** · S · deps: SSH5.2 · *(spec: circuit-topology §4)*
  - Acceptance: a literal → constant swap in `ItemCardStoreTests.cs`, `ItemSocketStoreTests.cs`, `GemTierTests.cs`, `ItemCardEndpointsTests.cs`, `ItemEquipEndpointsTests.cs`
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemCardStore|FullyQualifiedName~ItemSocketStore"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~GemTier|FullyQualifiedName~ItemCardEndpoints|FullyQualifiedName~ItemEquipEndpoints"`; verify-change
  - Files: the five named test files

- [x] **SSH5.5 — Remaining Server.Tests read the constant** · XS · deps: SSH5.2 · *(spec: circuit-topology §4)*
  - Acceptance: a literal → constant swap in `ItemInsertElementTests.cs`, `ItemPreviewEndpointsTests.cs`, `ItemWorkbenchEndpointsTests.cs`. The guard allowlist now holds only the named v1-history tests and doc comments
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemInsertElement|FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ItemWorkbenchEndpoints"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"`; verify-change
  - Files: the three named test files, `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`

- [x] **SSH5.6 — Python: one current-revision constant in `combogen/tuning.py`, imported by `basetypegen/tuning.py`** · S · deps: — · *(spec: circuit-topology §4)*
  - Acceptance: `SOCKETS_PATH` (combogen `:22`) is the one constant (still v1); `basetypegen/tuning.py:32` imports it. `test_base_types_gen.py` and `test_strain_splice_gen.py` read it
  - Acceptance: a Python literal-scan test finds no other `sockets.v{n}.json` path literal under `gk-forge/tools/seedsmith/seedsmith/`
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_base_types_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/tuning.py`, `gk-forge/tools/seedsmith/tests/test_base_types_gen.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`

- [x] **SSH5.7 — `publish.py --remove-key container.path:leaf`** · XS · deps: — · *(spec: circuit-topology §1)*
  - Acceptance: it removes an existing key in the new `v{n+1}`, and `publish_remove_key_refuses_an_absent_key` passes. The refusal discipline matches `--add-key` / `--rename-key`
  - Verify: `python -m pytest gk-core/tools/tuning/test_publish_add_key.py gk-core/tools/tuning/test_publish_remove_key.py -q`; verify-change
  - Files: `gk-core/tools/tuning/publish.py`, `gk-core/tools/tuning/test_publish_remove_key.py` (new)

- [x] **SSH5.8 — Circuits in the one evaluator; `SocketCircuitSize = 4`; the two parser rules** · M · deps: SSH1.1 · *(spec: circuit-topology §2–§3)*
  - Acceptance: `CombinationEvaluator` groups by `socketIndex / SocketCircuitSize` and runs its ordered pass per circuit, and `CombinationResult.Circuit` exists. `indices_three_and_four_never_combine`, `an_eight_socket_host_fires_two_independent_combinations`, `a_six_socket_host_has_one_complete_circuit_and_a_resonance_only_remainder` and `a_recipe_is_unordered_within_a_circuit` pass (fixture fills)
  - Acceptance: the structural `SocketCircuitSize` const has a why-comment; `Parse` throws on `ingredientCount != SocketCircuitSize` and on a resonance threshold `> SocketCircuitSize`. v1 still loads, and behaviour under v1 is unchanged (only circuit 0)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~SocketGeometry|FullyQualifiedName~ComboMatcher"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs`, `tests/FusionRpg.Core.Tests/Items/CombinationEvaluatorTests.cs`

- [x] **SSH5.9 — combo-bind carries the circuit: the same word in two circuits is two contributions** · S · deps: SSH4.6, SSH5.8 · *(spec: combo-bind §2–§3 tests)*
  - Acceptance: `ComboBindTarget.Circuit` comes from `CombinationResult.Circuit`; `the_same_word_in_two_circuits_is_two_contributions` (eight-socket fixture → two SourceIds `#c0` / `#c1`)
  - Acceptance: `one_identity_per_circuit_is_the_only_limit`: two Strains satisfiable in one circuit → one binds; in two circuits → both bind
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~EquipProjectionSockets|FullyQualifiedName~EquipAtomSourceId"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/EquipProjector.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs`, `tests/FusionRpg.Core.Tests/Items/EquipProjectionSocketsTests.cs`
  - ✅ **DONE 2026-09-22 (lane `ssh29`).** `ComboBindTarget.Circuit` is the evaluator's own
    `CombinationResult.Circuit`; the read side passes it through, so the SourceId carries `#c{circuit}`.
    `the_same_word_in_two_circuits_is_two_contributions` (8 sockets → two bindings/SourceIds differing
    only by `#c0`/`#c1`) and `one_identity_per_circuit_is_the_only_limit` (4 sockets → one identity;
    8 sockets → both, one per circuit) pass. Filter 13/0, verify-change exit 0 (Core.Items 1404/0).
    Evidence: `tasks/evidence-fragments/SSH5.9.md`.

- [x] **SSH5.10 — THE FLIP: publish `sockets.v2.json`, `SocketMaxCeiling` 8, both constants → v2 (one commit)** · M · deps: SSH4.1, **SSH4.2 (H3)**, SSH5.1–SSH5.8 · *(spec: circuit-topology §1–§2, §4)* · **parent H7**
  - Acceptance: `python tools\tuning\publish.py sockets …` writes v2: ceilings 0–8 per spec §1, **`head-guard` 4 (R11)**, `rarityGrant` `0/0 · 0/2 · 2/4 · 2/6 · 4/8`, and `--remove-key` for `maxCombosPerActor` / `…Note` (R12). v1 is untouched
  - Acceptance: `SocketLimits.SocketMaxCeiling` 4 → 8. `SocketTuningFiles.Current` and the Python constant name v2 **in the same commit**. `the_current_socket_revision_carries_no_combination_cap`, `sockets_zero_to_eight_are_capacity_for_every_role_ceiling`, `head_guard_ceiling_is_read_from_tuning_only`, `a_four_socket_helm_has_one_complete_circuit_and_no_remainder` pass
  - Acceptance: `existing_items_keep_their_socket_rows`; `dotnet run --project gk-forge/tools/ItemSeedValidator` green against v2 (the un-restamped corpus is within v2 ceilings)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~SocketAllowance|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore|FullyQualifiedName~ItemCardStore"`; `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~GemTier|FullyQualifiedName~ItemWorkbenchEndpoints|FullyQualifiedName~ItemPreviewEndpoints"`; SP `gk-forge/tools/seedsmith/tests/test_base_types_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py`; verify-change
  - Files: `gk-core/data/tuning/sockets.v2.json` (published), `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `tests/FusionRpg.Core.Tests/Items/SocketGeometryTests.cs`

- [x] **SSH5.11 — `basetypegen/resocket.py`: the deterministic re-stamp verb (dry run)** · S · deps: SSH5.6 · *(spec: circuit-topology §5)*
  - Acceptance: for every base-type row it recomputes `socketMax` through `resolve_socket_max(role, band, seq)` under the current revision. Only that field changes; id, name, class, band and flavour are kept, and a ledger amendment is recorded. No model call. `--dry-run` prints the diff
  - Acceptance: `resocket_is_deterministic_and_changes_only_socket_max` (the reslate precedent)
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_base_types_gen.py`; `cd tools\seedsmith; python -m seedsmith.adapters.items.basetypegen.resocket --dry-run`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/basetypegen/resocket.py` (new), `gk-forge/tools/seedsmith/tests/test_base_types_gen.py`


  - **OWNER HALF DONE 2026-09-21 (manager-executed; owner answered "Run SSH5.12 now").** Preflight
    re-printed and identical to the authorized reading (total 1158 / unchanged 321 / resocketed 837),
    then `--write`: 60 corpus files, diff is `socketMax` + the per-file `_meta.amendments` record only.
    Validator PASS (3957 entries / 1013 files / 2591 warnings, 0 SocketMax findings); Core
    StrainSpliceGrid|BaseTypeCorpus 30/0; seedsmith base-types 69 passed. Evidence:
    `tasks/evidence-fragments/SSH5.12.md`.
  - **This row stays OPEN for its own second acceptance line:** the follow-up edit tightening SSH5.1's
    contract from subset to `the_corpus_host_set_equals_the_tuning_host_set` (C# + Python) —
    `test_strain_splice_gen.py::test_the_corpus_host_set_is_a_subset_...` now fails on its stale
    "corpus max == ingredientCount" clause (4 != 8) after the re-stamp, which is that edit's job.
    Routed to the fresh lane in the manager's brief; it must land in the same commit family as this
    corpus or the corpus ships with a red test.
    **LANDED 2026-09-21 by lane `ssh28`** — both ports now assert set EQUALITY (the corpus reaches 4+ in
    exactly the 11 roles v2 admits); Python 69 passed, Core 30/0, Core.Tests via verify-change 15075/0,
    validator PASS 3957/1013/2591. Evidence: `tasks/evidence-fragments/SSH5.12.md` § "Second acceptance line".
  - **`ssh27` was drained** (input 983 / output 3 tokens per segment, `exitCodes [0,0,0]`), which is
    why the owner job ran on the manager's plane rather than waiting on that lane.
- [x] **SSH5.12 — OWNER-RUN: `resocket --write` over `gk-data/packs/fusion/data/seed/items/base-types/**` (ask-first corpus rewrite)** · owner · deps: SSH5.10, SSH5.11 · *(spec: circuit-topology §5, Boundaries)*
  - Acceptance (owner's run output): the owner reviews the dry-run diff, then `--write` re-stamps only `socketMax`; `no_base_type_exceeds_its_role_ceiling_after_resocket` (ItemSeedValidator against v2) is green
  - Acceptance: the follow-up agent edit tightens SSH5.1's corpus contract from subset to `the_corpus_host_set_equals_the_tuning_host_set` in C# and Python, and it is green
  - Acceptance: if the owner declines, the task closes as declined, the subset contract stays, and SSH5.13 does not run (plan Defaults)
  - Verify: `dotnet run --project gk-forge/tools/ItemSeedValidator`; `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~BaseTypeCorpus"`; SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`
  - Files: `gk-data/packs/fusion/data/seed/items/base-types/**` (re-stamped by the verb), `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`

- [x] **SSH5.13 — OWNER-RUN (combination-regen R11 step): helm-host re-run under v2** · owner · deps: SSH5.12, SSH2.5, SSH2.7 · *(spec: combination-regen "The helm joins the host set")*
  - Acceptance (owner's run output): `generate --kind combination --shape strain|splice --write --retry-blocked` under v2, with `head-guard` offered by derivation. Authored cells are not re-run
  - Acceptance: `--metric Coverage/HostRoleDiversity` is printed across weapon / chest / helm / other roles, as a reading. The still-blocked report is re-printed, with every cell `entry` or listed by id (R13)
  - Acceptance: after the corpus moves, `the_shipped_corpus_has_no_refusal` (SSH3.3/SSH4.4) is still green
  - Verify: `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate --metric Coverage/HostRoleDiversity`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus"`
  - Files: `gk-data/packs/fusion/data/seed/items/combinations/*.json`, `combination-gen.ledger.json`, still-blocked report file
  - **RAN 2026-09-21 by lane `ssh28` (manager-authorized).** strain planned 5 → persisted 2 / blocked 3;
    splice planned 2 → persisted 1 / blocked 1; `head-guard` offered by derivation in every pass
    (`hostRoles` prints all 11, `geometricCombosPerActor: 11`). HostRoleDiversity: strain core-guard
    593‰ / armament-primary 343‰ / none 62‰ / **helm 0‰**; splice core-guard 545‰ / armament-primary
    439‰ / manipulator 15‰ / **helm 0‰**. Final corpus: 32 strain + 66 splice entries + 4 reported = **102
    cells**, 0 unaccounted; validator **PASS 3960/1013/2589**; Core `CombinationCorpus` 6/0. Evidence:
    `tasks/evidence-fragments/SSH5.13.md`.

- [x] **SSH5.13-P1 — the combogen authoring graph validates schema + vocabulary but NOT the naming contract** · S · deps: SSH5.13 · *(found by lane `ssh28` 2026-09-21, driving the R11 re-run)*
  `workflow/graphs/item_combination.py`'s validators are `answer_matches_schema`, `answer_declares_content`,
  `answer_stays_in_vocabulary` — none checks the grammar the C# gate enforces
  (`NamingCheck.cs:167` `NameGrammarViolation`, `:184` `FusionNotDecomposable`, `:159` `InventedConnective`).
  The collision half is now guarded (`answer_reuses_a_shipped_idea` + `ItemSeedValidator --normalize-names`,
  landed with SSH5.13); the grammar half is not, so a `--write`/`--retry-blocked`/`--overwrite` run can still
  persist a name the validator rejects. Measured live: the cell `combo.strain-ferocity-balance` persisted
  `Ironstead`, then `Ironheart`, both refused `FusionNotDecomposable` (a one-word compound that does not
  decompose into two pool words) — three authoring passes spent, the cell ends `escalated` and is now reported
  by id. **Remedy:** the same authority pattern — a `NamingCheck`-backed validator in the graph (a
  `--check-names` mode beside `--normalize-names`), never a Python mirror of the patterns. `NAMING_GRAMMAR_RULES`
  is already in the authoring brief (`combogen/brief.py:108`), so the fix is the check + its heal feedback.
  **Reproduce:** `python -m seedsmith items generate --kind combination --shape strain --overwrite combo.strain-ferocity-balance --write --allow-production-tree` then `dotnet run --project gk-forge/tools/ItemSeedValidator`.
  - **DONE 2026-09-21 by lane `ssh28` (the lane that filed it).** `ItemSeedValidator --check-names` (the
    validator's own `NamingCheck.CandidateNameDefects`), `name_repair.name_defects()` as its authority
    wrapper, and `answer_uses_a_legal_name` in the graph armed by `_cmd_items_combination_write` — the
    same pattern the shipped-name guard uses. `test_combogen.py` 34/0 (the graph refuses `Ironstead` and
    escalates rather than persisting; a `blocked` answer is never judged on a name; no authority ⇒ the
    check is off, never guessed). The tool's own tests 97/0 and the corpus PASS. Evidence:
    `tasks/evidence-fragments/SSH5.13-P1.md`.

### Checkpoint 4 — module 5 exit and module 2 exit
- [ ] `sockets.v2.json` is the only revision any reader loads as current; the literal guard is green; v1 is untouched
- [ ] The evaluator runs per four-socket circuit; indices 3 and 4 never combine; the structural consts have comments and throwing mirrors
- [ ] The base-type corpus was re-stamped by the verb (or the owner declined it, and the subset contract stands)
- [ ] The R11 re-run ran; `Coverage/HostRoleDiversity` is printed; every grid cell is `entry` or reported by id (R13)
- [ ] Full suite once (Core, Data, Server, a tool and seedsmith all changed; AGENTS.md point 2): `.\scripts\test-fast.ps1 -AllDefault` or `deploy-play.ps1 -FullTestSuite`

---

## Wave 6 — `combo-budget` (measure power against price; R12, R20)

- [x] **SSH6.1 — Circuit-aware geometry reading on both ports, with a parity test** · S · deps: SSH5.8, SSH4.2 · *(spec: combo-budget §2)*
  - Acceptance: C# `SocketGeometry.GeometricCombinationCeiling(tuning, roles)` and Python `geometric_combo_ceiling` both compute `Σ floor(ceiling/SocketCircuitSize)`, plus `reachableCeiling`. Neither is compared to anything
  - Acceptance: `geometric_ceiling_counts_complete_circuits_not_roles` (8→2, 6/4→1, 3→0, fixture); geometry parity on the shipped file (`python_and_csharp_readings_agree_on_the_shipped_tuning`)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketGeometry"`; SP `gk-forge/tools/seedsmith/tests/test_combogen.py`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketGeometry.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `tests/FusionRpg.Core.Tests/Items/SocketGeometryTests.cs`, `gk-forge/tools/seedsmith/tests/test_combogen.py`

- [x] **SSH6.2 — `ComboPricing`: power, price floor, rarity reference, and the bound (checked `long`, cross-multiplied)** · M · deps: SSH4.3, SSH6.1 · *(spec: combo-budget §1)*
  - Acceptance: power comes from `ActorPowerCache.Compose` over `ComboContainerBuild` atoms; `PriceFloorSouls` is taken over the admitting rungs with the best-rolled chassis. The reference comes from `PriceReferenceSlate` / `elevate`, and prices from `MaterialRecipeCatalog.Resolve`. No second curve
  - Acceptance: edge rules: `the_comparison_is_cross_multiplied`, `a_rarity_step_that_buys_nothing_is_excluded_by_name` (all excluded → refused), the top rung gives no step, a zero floor is refused by name, and `price_floor_takes_the_cheapest_admitting_rung_and_best_rolled_chassis`
  - Acceptance: `a_combination_cheaper_than_the_rarity_route_fails_the_report_by_cell` (fixture); `python gk-core/scripts/audit-overflow.py` is clean for the new file
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboPricing"`; `python gk-core/scripts/audit-overflow.py`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs` (new), `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs` (new)
  - **DONE 2026-09-21 by lane `ssh28`.** `ComboPricing` + 7 tests, on the real tuning / ladder / materials
    catalog. Every term reused, never re-derived: power = `ActorPowerCache.Compose` over
    `ComboContainerBuild` atoms, price = `MaterialRecipeCatalog.Resolve`'s souls leg, the rarity route =
    `PriceReferenceSlate` Δ over `elevate`, geometry = `SocketCircuitSize` + the tuning's `rarityGrant`.
    The verdict is the spec's own cross-multiplied `long` inequality (`Passes`), with the quotients kept
    as printed readings only; a zero floor, a step that buys nothing/all excluded, and a host role that
    cannot hold the word are all refused BY NAME. `audit-overflow` clean for the new file; Core 15082/0.
    Evidence: `tasks/evidence-fragments/SSH6.2.md`.

- [x] **SSH6.3 — Derived levers per failing cell: bore / imbue / `forge-gem` souls (R20)** · S · deps: SSH6.2 · *(spec: combo-budget §1 "Which lever", §3)*
  - Acceptance: for each failing cell, it names the leg(s) on its floor route and derives the smallest souls coefficient that passes. Overall it derives the smallest bore/imbue/`forge-gem` coefficients that pass every cell. A cell no leg can fix is listed by id
  - Acceptance: `a_cell_with_no_bore_or_imbue_on_its_floor_route_names_forge_gem_as_its_lever`, `the_derived_forge_gem_coefficient_makes_a_gem_only_cell_pass` (one below still fails), `the_derived_coefficient_makes_every_cell_pass`
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboPricing"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricing.cs`, `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs`
  - **DONE 2026-09-21 by lane `ssh28`.** `ComboPricingLever` + `ComboPricing.Derive` + a `Lever` on every
    `ComboPriceLeg`: each failing cell gets the levers on its own floor route, the cheapest by name, and
    its required coefficient (closed-form `ceil(need · 1000 / legTotal)`, rounded up); each lever gets the
    smallest coefficient passing every cell it can move, and a cell no lever can move is listed by id. A
    lever whose souls leg is not `rung`-linear is refused by name. 11 ComboPricing tests / 0, Core 15086/0,
    `audit-overflow` exit 0 with no finding naming the file. Evidence: `tasks/evidence-fragments/SSH6.3.md`.

- [x] **SSH6.4 — `python -m seedsmith items combo-budget --report` (the readable form; exits non-zero on a failing cell)** · M · deps: SSH6.3 · *(spec: combo-budget §3)*
  - Acceptance: per frame it prints both geometry readings, the per-role circuit count and the enabled words per admitted role (helm included). Per cell it prints power, `priceFloor` and every leg, the ratio, the reference, and pass/fail. On failure it prints the derived coefficients. It asserts no reading's size
  - Acceptance: `power(c,k)` comes from the one C# computation (default: a JSON dump written by `ComboPricing`, see plan Defaults), never a Python re-implementation of `Compose`. Parity test on price floor
  - Acceptance: the owner reads a run of the report on the shipped files; it either passes or names the cells SSH8.5 fixes
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_combogen.py`; `cd tools\seedsmith; python -m seedsmith items combo-budget --report`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`, the C# power-dump entry point
  - **DONE 2026-09-21 by lane `ssh28`.** Entry point chosen: `ItemSeedValidator --combo-budget-dump`
    (beside `--collision-groups`/`--normalize-names`), read by `combogen.tuning.combo_budget_dump()` and
    rendered by `items combo-budget --report`. Shipped run: **35 priced cells, 25 FAIL, 161 unpriced**,
    reference `sprout -> grafted` (1100 power / 120 souls), derived `forge-gem 30 -> 415`; per-frame
    readings over the corpus's own two frames, per-role circuits and enabled words (helm 4/1/0). Parity
    test re-derives `gem(t)` in Python against the dump leg by leg. `test_combogen.py` 31/0; Core 15086/0;
    ItemSeedValidator.Tests 97/0. Evidence: `tasks/evidence-fragments/SSH6.4.md`.

- [x] **SSH6.5 — `no_combination_count_cap_exists`: a source scan that keeps R12 deleted** · XS · deps: SSH4.1, SSH4.2 · *(spec: combo-budget Testing)*
  - Acceptance: a scan of `src/`, `tools/` and `tests/` finds no `MaxCombosPerActor` / `max_combos_per_actor` / `SocketCombinationCap` identifier. The allowlist is `SOCKETS_OWNED_KEYS` and its C# mirror (the strain-splice ownership check), plus the v1 file
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ComboCountCap"`; verify-change
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/ComboCountCapGuardTests.cs` (new)
  - **DONE 2026-09-22 (lane `ssh29`) — the path was NOT hook-blocked.**
    `gk-core/tests/FusionRpg.Guard.Tests/ComboCountCapGuardTests.cs` was written and runs green:
    `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ComboCountCap"` → **2 passed / 0**.
    The allowlist is the five files a negative assertion cannot be written without naming — the guard
    itself, `combogen/tuning.py`'s `SOCKETS_OWNED_KEYS`, its C# mirror
    (`gk-core/tests/FusionRpg.Core.Items.Tests/Items/StrainSpliceGridTests.cs` — the row's own path was wrong,
    the project is `Core.Items.Tests`), the two R12 history tests
    (`.../SocketGeometryTests.cs`), and `test_strain_splice_gen.py` — and **a stale entry fails the
    guard**, so the list cannot grow into a licence. Nothing under `src/` names the identifier at all.
    Evidence: `tasks/evidence-fragments/SSH6.5.md`.

- [x] **SSH6.6 — `comboPricing` parse and `ComboPricingProvenance.Check` (pure)** · S · deps: SSH5.10 · *(spec: combo-budget §4–§5)*
  - Acceptance: `SocketTuning` parses the optional `comboPricing` and exposes `ComboPricingMeasuredAgainst`. `Check(measuredAgainst, loadedRevisions, corpusDigest, ladderRungs)` refuses by name when there is more than one rung and no provenance, or when any of the four fields differs
  - Acceptance: `a_multi_rung_ladder_refuses_unmeasured_pricing`, `a_ladder_published_after_the_measurement_is_refused_until_re_measured`, `provenance_versions_are_filename_revisions_not_the_internal_version_field`, `a_single_rung_ladder_loads_without_provenance`
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboPricing|FullyQualifiedName~SocketGeometry"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuning.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/ComboPricingProvenance.cs` (new), `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs`
  - **DONE 2026-09-21 by lane `ssh28`.** `SocketTuning` gains the ONE optional section
    (`ComboPricingMaxRatioToRarityRouteMilli` + `ComboPricingMeasuredAgainst`, the latter validated field
    by field with a SHA-256 digest shape check); `ComboPricingProvenance.Check` compares the FILENAME
    revisions, `circuitSize` and the corpus digest, refusing by name (`socket.combo-pricing-unmeasured`
    for a multi-rung ladder with no measurement, `socket.combo-pricing-stale` naming every field that
    moved). 5 tests, incl. the internal-`version`-vs-filename-revision case read off the real v1/v2 pair.
    `ComboPricing|SocketGeometry` 48/0; verify-change exit 0 with Core 15091/0; audit-overflow exit 0.
    Evidence: `tasks/evidence-fragments/SSH6.6.md`.

- [x] **SSH6.7 — Boot calls the provenance check once every input is loaded; corpus digest** · S · deps: SSH6.6, SSH4.4 · *(spec: combo-budget §4–§5)*
  - Acceptance: after sockets, strain-splice, materials and the accepted combination set load, the server computes the SHA-256 corpus digest (sorted ids, ingredient families, grants, host pins) and calls `Check`. Today's files, with no `comboPricing`, boot unchanged
  - Acceptance: `boot_refuses_a_revision_or_corpus_the_pricing_was_not_measured_against`, one field at a time, refused by name
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints|FullyQualifiedName~ComboPricing"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs` (digest helper), `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs` (new)
  - **DONE 2026-09-21 by lane `ssh28`.** `ComboPricingBoot` (new) + `CombinationCorpus.Digest` +
    `SocketTuningFiles.RevisionOf`; `Program.cs` captures the three tuning filenames it reads and, after
    the combination seed, computes the loaded revisions + digest over the ACCEPTED set and calls
    `RequireVerified` before anything binds. **SSH4.4 was not waited on** (recorded as a decision): the
    acceptance's four digest fields are readable from the accepted recipe set + `ReadGrants`, and the
    container build SSH4.4 adds accepts the same set, so the digest does not move with it. 3 boot tests +
    the row's filter 14/0 + the whole Server suite 761/0; verify-change exit 0 (Core 15091/0, Server 758/0).
    Evidence: `tasks/evidence-fragments/SSH6.7.md`.

- [x] **SSH6.8 — Publish `sockets` v3 `comboPricing` with the passing report's provenance, plus the BalanceGuard test (one commit)** · M · deps: SSH6.4, SSH6.5, SSH6.7, SSH2.5 and SSH5.13 (R5: measure the corpus that ships; a declined SSH5.13 counts as done), (SSH8.5 if the report was red) · *(spec: combo-budget §3–§4)* · **parent H7**
  - **DONE 2026-09-24 (mega-merge QC fix cycle 8).** The two-stage blocker chain is fully cleared: the
    measurement (SSH4.4 + SSH8.5) has been green since 2026-09-22, and this session ran the implementation
    the three dead opencode attempts could not land.
  - **What landed:** `ComboBudgetDump` now emits the `measuredAgainst` object (digest over the SAME accepted
    set through `CombinationCorpus.Digest`, revisions as FILENAME revisions); the report prints it; published
    `sockets.v3.json` via `publish.py sockets --add-key ":comboPricing=…"` with the **copied** reading
    (`socketsVersion` 3, `strainSpliceVersion` 1, `materialsVersion` 6, `circuitSize` 4, digest
    `ea0e042f98b0…`); `SocketTuningFiles.Current` and `combogen/tuning.py`'s `SOCKETS_PATH` → v3 in the same
    commit (H7). `[Trait("Category","BalanceGuard")] ComboPricingBoundGuardTests` recomputes the inequality
    over the shipped tuning + corpus (never trusting `measuredAgainst`) and is green.
  - **Proof:** `items combo-budget --report` exit 0 (164 priced, 0 refused); BalanceGuard test 1/1;
    `ComboPricingTests` 16/16; `ComboPricingBootTests` 3/3; seedsmith `test_combogen` + `test_base_types_gen`
    + `test_strain_splice_gen` 184 passed. Stale assertions that pinned the pre-publish state were rewritten
    structurally (contract, not a literal), per the validation standard.
  - Acceptance: `publish.py sockets --add-key ":comboPricing=…"` with `maxRatioToRarityRouteMilli` 1000 and `measuredAgainst` **copied from the passing report**, never typed. `SocketTuningFiles.Current` and the Python constant → v3 in the same commit
  - Acceptance: `[Trait("Category","BalanceGuard")] No_shipped_combination_is_a_cheaper_route_to_power_than_the_rarity_route` recomputes the inequality over the shipped tuning and corpus (it never trusts `measuredAgainst`) and is green in the same commit
  - Acceptance: the server boots against v3 with the check passing
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "Category=BalanceGuard&FullyQualifiedName~ComboPricing"`; `cd tools\seedsmith; python -m seedsmith items combo-budget --report` exits 0; verify-change
  - Files: `gk-core/data/tuning/sockets.v3.json` (published), `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs`
  - ⚠ **BLOCKED (external, 2026-09-21 by lane `ssh28`): the passing report this row requires does not
    exist.** Re-measured at this HEAD: `items combo-budget --report` exits 1 with **35 priced cells, 25
    FAIL, 161 unpriced** — the 25 need **SSH8.5**'s derived `materials` publish (this row's own dep:
    *"SSH8.5 if the report was red"*) and the 161 need **SSH4.4**'s remedy (the corpus regenerated with the
    current catalog, owner-run model calls, or the 10 missing atom families materialised). The two
    shortcuts — publish `comboPricing` with no `measuredAgainst` (the spec writes it "only when the report
    passes"), or a BalanceGuard test green over the 35 priced cells alone (an absent check must never read
    as a pass) — are refused. Everything else is ready: v3 is a mechanical `publish.py sockets --add-key`
    once the report is green, and the parser + boot check already exist. Evidence:
    `tasks/evidence-fragments/SSH6.8.md`.
  - ⏫ **RE-CHECKED 2026-09-22 by lane `ssh49f2`: the measurement blocker is LIFTED, and what remains is a
    FENCE blocker.** SSH4.4 and SSH8.5 both landed, and the report is green at this HEAD: `cd gk-forge/tools/seedsmith;
    python -m seedsmith items combo-budget --report` -> exit 0, `PASS — every cell is at or under the rarity
    route (164 priced, 0 refused)`. So this row is implementable now — but the publish and the guard test
    live in `gk-core/data/tuning/sockets.v3.json` (through `gk-core/tools/tuning/publish.py`),
    `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` and
    `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs`, none of which is in lane `ssh49f2`'s allowed
    paths. **Blocked on another lane (or a fence widening), not on the measurement any more.** Re-check
    table: `tasks/reports/ssh49f2-blocked-rows-recheck.md`.
  - **RESOLVED 2026-09-24 (mega-merge QC fix cycle 8):** the fence blocker is gone (single session on the
    mega-merge branch), and the implementation is complete. See the DONE note above. The prior deferral
    history is retained for the record.
  - **DEFERRED 2026-09-24 (owner: resume later):** three opencode attempts died on this row (ssh27b blocked on no-shell + fence, rescued as ssh27c which staged the full publish incl. BalanceGuard test, then destroyed by a manager cleanup-before-harvest defect; ssh27d failed on a CS0165 the staged test carried; ssh27e failed empty at 21 turns). Content survives only in `.claude/opencode-agents/agents/ssh27c/result.json` REPORT prose (v3 shape, reader switch, guard test, digest-fill procedure). Resume needs a shelved runtime or manager implementation.

### Checkpoint 5 — pricing measured
- [ ] The report exits 0 on the shipped files; any cell that failed on the way is named in the commit history together with the materials publish that fixed it
- [ ] The BalanceGuard test is green in CI (`Category=BalanceGuard`)
- [ ] `sockets.v3.json` provenance names filename revisions and the corpus digest; boot passes the check
- [ ] No count cap in code, tuning's current revision or tests (SSH6.5 green)

---

## Wave 7 — `tier-ladder` (better runes, better word)

- [ ] **SSH7.1 — `TierLadder` parse and load rules; a strain-splice current-revision constant (still v1); provenance from the ladder side** · S · deps: SSH5.2, SSH6.6 · *(spec: tier-ladder §1)*
  - Acceptance: `StrainSpliceTuning.Parse` reads `tierLadder`. v1's `minTierPlan` maps to a one-rung ladder (history keeps loading). The throw rules (not clamps) cover: ascending floors, strictly increasing rungs, `grantDelta` from 0 and increasing, and `max(baseTier)+top grantDelta+attunedTierBonus ≤ TierCount` (`a_ladder_whose_top_exceeds_the_atom_ladder_throws`, `a_non_ascending_or_non_increasing_ladder_throws`)
  - Acceptance: `SocketTuningFiles` gains the strain-splice constant, read at `gk-core/src/FusionRpg.Server/Program.cs:324` and by the combogen `STRAIN_SPLICE_PATH`. The literal guard is extended to `strain-splice.v{n}.json` (`every_reader_loads_the_current_strain_splice_revision`)
  - Acceptance: `a_multi_rung_ladder_needs_measured_combination_pricing`, `a_ladder_publish_invalidates_the_previous_measurement` (fixtures, through `ComboPricingProvenance.Check`)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing"`; `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceTuning.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `tests/FusionRpg.Core.Tests/Items/StrainSpliceGridTests.cs`
  - **PARTIAL 2026-09-21 by lane `ssh28` — the PARSER half landed, the guard line is the pipeline lane's.**
    `TierLadderRung` + the optional `recipe.tierLadder` (absent ⇒ the one-rung ladder the shipped floor
    describes), the five throw rules (ascending floors within and across rungs, `grantDelta` starting at 0
    and rising, the top rung inside the atom ladder), `SocketTuningFiles.StrainSplice` with its readers
    moved (the two runtime MESSAGES that named the literal were re-worded too), and 5 tests. Core
    StrainSpliceGrid|ComboPricing 43/0; Core (Release, whole) 15096/0; Server 764/0; the existing literal
    guard 2/2; seedsmith 104 passed. ⚠ **The acceptance's `every_reader_loads_the_current_strain_splice_revision`
    line is NOT done**: its file is `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`, a
    pipeline-protected path (same class as SSH6.5/CAI-guard-1), so **the row stays OPEN** on that line —
    recorded `blocked` in the ledger with the recommended guard shape. Evidence:
    `tasks/evidence-fragments/SSH7.1.md`.
  - ⏫ **RE-CHECKED 2026-09-22 by lane `ssh49f2`: still blocked on the SAME file.**
    `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` still carries only the
    `sockets\.v[0-9]+\.json` rule (`grep -n StrainSplice` there is empty), and that path is both
    pipeline-protected and outside lane `ssh49f2`'s allowed paths. Dependency: the pipeline lane that owns
    the guard file. Re-check table: `tasks/reports/ssh49f2-blocked-rows-recheck.md`.

- [x] **SSH7.2 — The one matcher returns a rung; `GrantedTier = baseTier + grantDelta + attuned`; the preview shows tier shortfalls** · M · deps: SSH7.1, SSH1.1 (R5 / SOLID) · *(spec: tier-ladder §2)*
  - Acceptance: `ComboMatcher.Match` claims on `(family, quantity)`, ignores `MinTier`, and returns the highest rung whose positional floor the sorted claimed tiers meet. The evaluator grants through the ladder, and `MatchResult` carries `Rung` and `TierShortfall(position, have, need)`
  - Acceptance: `rung_one_reproduces_the_shipped_flat_floor`, `higher_tier_gems_reach_a_higher_rung`, `every_permutation_of_a_fill_reaches_the_same_rung`, `attunement_adds_its_bonus_on_top_of_the_rung_and_never_gates`, `a_fill_below_rung_one_reports_tier_shortfalls_not_missing_families`
  - Acceptance: `rebalancing_the_ladder_needs_no_regeneration` (fixture v3 ladder; corpus unchanged, evaluator follows)
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~ItemSurface"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationEvaluator.cs`, `gk-core/src/FusionRpg.Core/Items/Surfaces/CombinationDistance.cs`, `tests/FusionRpg.Core.Tests/Items/ComboMatcherTests.cs`
  - **DONE 2026-09-21 by lane `ssh28`.** `Match` claims on `(family, quantity)` and reads the ladder
    positionally; `MultisetMatch.Rung` + `TierShortfall(position, have, need)`; the evaluator grants
    through the rung's `grantDelta`; the preview counts the rung shortfalls so distance-zero still means
    "the evaluator fires". No ladder passed = rung 1 with the recipe's own floors (expanded by
    `quantity`), which is why every pre-ladder caller is unchanged. 6 named tests + two self-found
    defects (per-row vs per-FILL floors; family-match-at-low-tiers is not distance zero). Core 15102/0,
    Server 764/0, verify-change exit 0. Evidence: `tasks/evidence-fragments/SSH7.2.md`.

- [x] **SSH7.3 — Generator: emit no tier numbers; combogen validates the ladder (mirrors C#)** · S · deps: SSH7.1 · *(spec: tier-ladder §3)*
  - Acceptance: `emit.py` stops zipping `minTierPlan` (`ingredient_rows`, `:104`) and stops writing `grantedTier` (`:133`, `:185`). Identical families fold to `{family, quantity}`. `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py:165` validates `tierLadder` with the same rules as C#
  - Acceptance: `the_emitted_entry_carries_no_tier_number` (fixture emit); ladder validation parity in `test_combogen.py`
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`, `gk-forge/tools/seedsmith/tests/test_combogen.py`
  - **DONE 2026-09-21 by lane `ssh28`.** `IngredientRow` is `(family, quantity)` (identical families
    fold), `assemble_entry` writes no `grantedTier` (the `granted_tier` helper is deleted with it), and
    `combogen/tuning.py` mirrors the C# ladder rules — the shipped one-rung mapping, a published ladder
    replacing it whole, and SEVEN refusal cases matching the C# validator's. The shipped corpus is
    untouched by this row (SSH7.4's re-emit is what rewrites it; SSH7.5/7.6 flip the consumers).
    `test_strain_splice_gen.py` + `test_combogen.py` 108 passed / 7 subtests; the items suites 231
    passed; the validator stays PASS at 3978 entries. Evidence: `tasks/evidence-fragments/SSH7.3.md`.

- [x] **SSH7.4 — `combogen-reemit` verb: re-emit from the run ledger, no model call** · S · deps: SSH7.3 · *(spec: tier-ladder §3)*
  - Acceptance: it re-emits the corpus through `entries_from_ledger` (`gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py:275`), and `_meta.amendments` records the re-emit. No model call, no hand edit
  - Acceptance: `reemit_is_byte_identical_on_a_second_run`, `reemit_preserves_every_model_answer` / `reemit_changes_no_model_answer` (families, grants, pins, names)
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`; `cd tools\seedsmith; python -m seedsmith items combogen-reemit --dry-run`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/report/cli.py`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/authored.py`, `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`
  - **DONE 2026-09-21 by lane `ssh28`.** `authored.reemit_entry`/`reemit` rebuild ledger entries through
    the current emit shape (model answers verbatim, no tier), and `items combogen-reemit
    --dry-run|--write` drives it with a `_meta.amendments` batch on a write. Dry run: strain 32/32 and
    splice 66/66 entries changed, nothing written. Tests: byte-identity on a second run, every model
    answer preserved, and the verb dry-running by default; 111 passed / 11 subtests. The corpus write
    itself is SSH7.6's (after SSH7.5 flips the C# consumers). Evidence: `tasks/evidence-fragments/SSH7.4.md`.

- [x] **SSH7.5 — C# drops the corpus's tier fields: `BaseTier` from tuning, the base-tier rule deleted, `KindCatalog` no longer requires `grantedTier`** · S · deps: SSH7.1, SSH3.1 · *(spec: tier-ladder §3)*
  - Acceptance: `CombinationCorpus` fills `ComboRecipe.BaseTier` from `StrainSpliceTuning.BaseTierFor`, and `ComboIngredient.MinTier` is written as `0` (default until SSH7.8). `strainsplice.base-tier-not-tunable` (`StrainSpliceGrid.cs:164`) is deleted, not left as dead code
  - Acceptance: `KindCatalog.cs:132` removes `grantedTier` from required; extra still allows it until SSH7.6. The existing corpus still validates
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus|FullyQualifiedName~StrainSpliceGrid"`; `dotnet run --project gk-forge/tools/ItemSeedValidator`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/StrainSpliceGrid.cs`, `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`, `tests/FusionRpg.Core.Tests/Items/CombinationCorpusTests.cs`
  - **DONE 2026-09-21 by lane `ssh28`.** `ToRecipes` fills `BaseTier` from tuning and writes `MinTier = 0`
    (the row's tier fields are parsed and deliberately unread until SSH7.6 removes them); `ComboRecipe`
    gains `BaseFloors` (rung 1 from the tuning's ladder at import) so the no-ladder matcher path keeps
    its exact behaviour, and it now REFUSES a non-empty recipe with no floors; the
    `strainsplice.base-tier-not-tunable` const and its check are deleted with an absence assertion;
    `KindCatalog` no longer requires `grantedTier` (still allowed in `extra`). Core 15103/0, Server
    764/0, validator tests 97/0, validator PASS 3978, verify-change exit 0. Evidence:
    `tasks/evidence-fragments/SSH7.5.md`.

- [x] **SSH7.6 — Run `combogen-reemit --write`: the shipped corpus carries no tier number** · S · deps: SSH7.2, SSH7.4, SSH7.5 · *(spec: tier-ladder §3)*
  - Acceptance: a deterministic re-emit (the agent runs it; no model call). No combination row carries `minTier` or `grantedTier`. `KindCatalog` extra drops `grantedTier`
  - Acceptance: under v1 (one rung), behaviour is unchanged: `the_shipped_corpus_has_no_refusal` and `rung_one_reproduces_the_shipped_flat_floor` are green; the corpus digest changes, so the boot provenance check needs SSH7.7's re-measure in the same commit **if** SSH6.8 has already landed (suggested: run SSH7.6 before SSH6.8, so one measurement covers it)
  - Verify: `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate`; `dotnet run --project gk-forge/tools/ItemSeedValidator`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~CombinationCorpus"`; verify-change
  - Files: `gk-data/packs/fusion/data/seed/items/combinations/*.json` (re-emitted), `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs`
  - **DONE 2026-09-21 by lane `ssh28`.** The re-emit ran: **32 strain + 66 splice** rows re-shaped, **0**
    entries carrying `minTier`/`grantedTier`, amendments `combogen-reemit/{strain,splice}-1` recorded;
    `KindCatalog`'s `extra` narrowed in the same commit with a new test proving a tier-carrying row is
    now refused. Two stale readers updated (the `GemTierTests` hand-rolled recipe mapper and its
    minTier-range test; the validator's conforming fixture). Core 15103/0, Server 764/0, validator tests
    98/0, validator PASS 3978, seedsmith gate 57/607/153 with 0 combination gaps. The corpus paths have no
    verification-boundary owner row (TVB-F14, already filed), so the corpus evidence is those direct runs.
    Evidence: `tasks/evidence-fragments/SSH7.6.md`.

- [ ] **SSH7.7 — THE LADDER FLIP: publish `strain-splice.v2.json`, re-measure, republish sockets provenance (one commit)** · M · deps: SSH6.8 (R5), SSH7.6 · *(spec: tier-ladder §1)* · **parent H7**
  - Acceptance: `publish.py strain-splice --add-key "recipe:tierLadder=[…]" --remove-key recipe:minTierPlan`, where rung 1 equals today's floor. The strain-splice constant (C# and Python) → v2 in the same commit
  - Acceptance: `combo-budget --report` prices rungs 2..n and exits 0 (if red: SSH8.5's derived publish first). The next `sockets` revision republishes `measuredAgainst` with the new `strainSpliceVersion` and corpus digest, copied from the report
  - Acceptance: the server boots, the provenance check passes, and the BalanceGuard test is green; `python gk-core/scripts/audit-magic-numbers.py --summary` shows no new literal
  - Verify: `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ComboMatcher|FullyQualifiedName~CombinationEvaluator|FullyQualifiedName~StrainSpliceGrid|FullyQualifiedName~ComboPricing"`; `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"`; verify-change
  - Files: `data/tuning/strain-splice.v2.json` (published), `data/tuning/sockets.v{n}.json` (published), `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py`
  - ⚠ **BLOCKED (external, proved 2026-09-21 by lane `ssh28`): the ladder publish and its measurement are
    one atomic act, and the measurement is red.** `A_multi_rung_ladder_needs_measured_combination_pricing`
    (1 passed / 0) pins `socket.combo-pricing-unmeasured` for a two-rung ladder with no `measuredAgainst`,
    and the spec writes that provenance "only when the report passes" — so publishing rungs 2..n now would
    make the server refuse to boot, the opposite of this row's own acceptance line. The report reads
    **47 cells cheaper than the rarity route, 126 unpriced** (exit 1): the 47 need **SSH8.5**'s derived
    `materials` publish and the 126 need **SSH4.4**'s owner-run atom/corpus remedy — SSH6.8's two
    blockers, which this row's own dep list names. Evidence: `tasks/evidence-fragments/SSH7.7.md`.
  - ⏫ **RE-CHECKED 2026-09-22 by lane `ssh49f2`: the measurement is GREEN, the dependency chain is not.**
    `combo-budget --report` now exits 0 (`PASS — every cell is at or under the rarity route (164 priced, 0
    refused)`), so the "measurement is red" half of this blocker is history. What still holds: this row's
    dep **SSH6.8 is not done** (it is now fence-blocked, see its row), and the ladder publish itself needs
    `data/tuning/strain-splice.v2.json` + `data/tuning/sockets.v{n}.json` +
    `gk-forge/tools/seedsmith/…/combogen/tuning.py` — outside lane `ssh49f2`'s allowed paths. **Blocked on SSH6.8
    and on another lane/fence widening.** Re-check table: `tasks/reports/ssh49f2-blocked-rows-recheck.md`.
  - **One defect found and fixed here (not a bookkeeping note — it is in the same commit):** the pricing
    dump priced four **tier-0** gems after the re-emit (`ComboBudgetDump` read the recipe rows' `MinTier`,
    which SSH7.5/7.6 zeroed), so the report read a meaningless `0 failing / 196 unpriced`. It now takes
    its tiers from `ComboRecipe.BaseFloors` — the ladder's rung-1 floors — which is what makes the
    47/126 reading above honest.

- [x] **SSH7.8 — DDL: drop `socket_combo_ingredient.min_tier` and `ComboIngredient.MinTier`** · lane · deps: SSH7.6 · *(spec: tier-ladder §4)* — ✅ **OWNER APPROVED 2026-09-21**: execute the drop (H2 — migration before writes to the re-keyed table); `SSH7.5`'s write-0-never-read default retires with it
  - Acceptance (after the owner approves the ask-first DDL): the column leaves the columns and the primary key (`RpgStore.Sockets.cs:69`, `:71`), and the content table is dropped and re-seeded at boot. `ComboIngredient` loses `MinTier` (`SocketModel.cs:113`)
  - Acceptance: until then the default holds: the column stays, written `0` and never read (SSH7.5)
  - Verify: `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~ItemSocketStore"`; `.\scripts\guard-dal.ps1`; verify-change
  - Files: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Sockets.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/ComboMatcher.cs`, `gk-core/tests/FusionRpg.Data.Tests/Items/ItemSocketStoreTests.cs`
  - **DONE 2026-09-22 (lane `ssh29`).** The ingredient table is re-keyed `(combo_id, family_id, min_tier)` →
    `(combo_id, family_id)`: a boot that still sees `min_tier` DROPs the table before any write and the
    same `CREATE` rebuilds it, then `CombinationBoot` re-seeds. `ComboIngredient` and `MissingIngredient`
    lost their tier members; `ComboRecipe.BaseFloors` is the only floor carrier, and it is now PERSISTED
    (`socket_combo_recipe.base_floors`, additive `EnsureColumn`) because the store round-trip is the
    no-ladder caller — without it every store-loaded recipe throws. New test proves the re-key over a
    hand-seeded pre-init hot DB (columns exactly `combo_id, family_id, qty`; the pre-migration row is gone;
    re-seed lands on the new key; second boot does not drop). ItemSocketStore 13/0, guard-dal OK,
    verify-change exit 0 (Core.Items.Tests 1396/0, Server 788/0). Evidence: `tasks/evidence-fragments/SSH7.8.md`.

---

## Wave 8 — `socket-pricing` (the chassis is a plan; price carries scarcity)

- [x] **SSH8.1 — Deterministic imbue emitter `recipegen/imbue.py`** · S · deps: — · *(spec: socket-pricing §1)*
  - Acceptance: one row per `(bore frame, concrete element)` (`omni` excluded), built from bore's substrate + catalyst lines and bands verbatim plus `essence.<element>`, with a derived name. Idempotent. `opvocab.SUPPORTED_FOR_GENERATION` is not widened
  - Acceptance: `imbue_rows_are_derived_and_idempotent`, `imbue_is_never_offered_to_the_model`, `every_imbue_row_names_a_concrete_element_essence`, `omni_is_never_an_imbue_element`
  - Verify: SP `gk-forge/tools/seedsmith/tests/test_recipes_gen.py`; verify-change
  - Files: `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/imbue.py` (new), `gk-forge/tools/seedsmith/seedsmith/adapters/items/recipegen/run.py`, `gk-forge/tools/seedsmith/tests/test_recipes_gen.py`
  - **DONE 2026-09-21 by lane `ssh28`.** One row per `(bore frame, concrete element)` (3 x 6 = **18**
    planned today), built from the bore row's lines + band verbatim plus `essence.<element>`, derived
    name, idempotent on `(frame, element)`; called from the existing `--emit-deterministic` step.
    `opvocab.OPERATION_OUTPUT_KIND` was NOT touched — that map IS the generation gate, so the emitter's
    `outputKind` is stated locally with that reason and `require_supported_operation("imbue")` still
    raises (`test_recipes_gen.py` 62/0, incl. the pre-existing refusal test). The dry run plans 18 and
    writes nothing; the write is SSH8.2's. Evidence: `tasks/evidence-fragments/SSH8.1.md`.

- [x] **SSH8.2 — Emit the imbue rows into `recipes.json` (the agent runs it if the step is model-free; otherwise the owner does)** · S · deps: SSH8.1 · *(spec: socket-pricing Regenerate)*
  - Acceptance: `generate --kind recipe --dry-run`, then `--write`, with the imbue emitter step; `_meta.amendments` records the batch. No row is added by hand
  - Acceptance: the `--gate` check, `ItemSeedValidator`, and the server's boot import of `MaterialRecipeCatalog` (refuses unpayable rows by name) are all green
  - Verify: `cd tools\seedsmith; python -m seedsmith check ..\..\data\seed\items --adapter items --gate`; `dotnet run --project gk-forge/tools/ItemSeedValidator`
  - Files: `gk-data/packs/fusion/data/seed/items/recipes/recipes.json` (generated)
  - **DONE 2026-09-21 by lane `ssh28`, together with SSH8.3 (their dep runs both ways: the rows cannot
    ship before an executor, and the executor is pointless before the rows).** The write adds 18 imbue
    rows (`recipe.070`–`recipe.087`) and the `recipegen/deterministic-emit-1` amendment; validator PASS
    3978 entries; seedsmith gate 57/607/153 with 0 imbue gaps. Evidence:
    `tasks/evidence-fragments/SSH8.3.md`.

- [x] **SSH8.3 — The essence must name the element; bore → imbue → fill end to end** · S · deps: SSH8.2 · *(spec: socket-pricing §2–§3)*
  - Acceptance: `SocketImbue` refuses `ContentRuleViolated{socket.imbue-element-mismatch}` (a new rule id; the enum stays closed): `imbuing_with_a_mismatched_essence_is_refused_by_name`
  - Acceptance: `a_chaff_chassis_can_be_bored_imbued_and_filled_end_to_end` (real endpoints, real recipes, real stock debit, read back through `GetSockets`); `bore_and_imbue_cost_more_on_a_higher_rung_and_succeed_on_both` (D23); `imbue_legs_equal_bore_legs_plus_essence` stays green
  - Verify: `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemWorkbenchEndpoints"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~MaterialCorpus"`; verify-change
  - Files: `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `gk-core/src/FusionRpg.Core/Items/Sockets/SocketModel.cs`, `gk-core/tests/FusionRpg.Server.Tests/ItemWorkbenchEndpointsTests.cs`
  - **DONE 2026-09-21 by lane `ssh28` (with SSH8.2's write, one commit).** `SocketRules.ImbueElementMismatch`
    + the essence/element check in `ItemWorkbench.SocketImbue` (its stale "no recipe authors the verb" doc
    refreshed), and three tests: the mismatch refused by name with nothing spent, a chaff chassis bored →
    imbued → filled with a real debit and read back through `GetSockets`, and both verbs dearer at the top
    rung while succeeding on both hosts. `EveryRecipeOperationWithRowsHasAnExecutorExceptElevate` gains
    `imbue` in the same commit. Workbench filter 62/0; Server suite 764/0; Core MaterialCorpus 20/0;
    validator PASS 3978; verify-change exit 0. Evidence: `tasks/evidence-fragments/SSH8.3.md`.

- [ ] **SSH8.4 — A materials current-revision constant (still v1); readers and the literal guard move to it** · S · deps: SSH5.2 · *(spec: socket-pricing §5 "every reader moves")*
  - Acceptance: `SocketTuningFiles` gains the materials constant, read at `gk-core/src/FusionRpg.Server/Program.cs:301` and by `ItemWorkbench.cs` and the tests that mean the shipped file (`MaterialCorpusTests`, `MaterialSpendTests`, `ItemWorkbenchEndpointsTests`). Behaviour is unchanged
  - Acceptance: `every_reader_loads_the_current_materials_revision`: the literal guard is extended to `materials.v{n}.json`
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral"`; `dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~MaterialCorpus"`; verify-change
  - Files: `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/src/FusionRpg.Server/ItemWorkbench.cs`, `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs`, `tests/FusionRpg.Core.Tests/Items/MaterialCorpusTests.cs`
  - **PARTIAL 2026-09-21 by lane `ssh28` — the constant + readers landed, the literal-guard line is the
    pipeline lane's.** `SocketTuningFiles.Materials` names the revision the readers already loaded (no
    behaviour change), `Program.cs` reads it, the seedsmith `recipegen/brief.py` constant documents itself
    as its mirror, and `MaterialCorpusTests` reads it. Core 15103/0, the materials/sockets filters 47/0, the
    existing literal guard 2/2, validator PASS 3978. ⚠ **`every_reader_loads_the_current_materials_revision`
    is NOT done** — `gk-core/tests/FusionRpg.Guard.Tests/**` is pipeline-protected, so **the row stays OPEN** on that
    line with the recommended guard shape in `tasks/evidence-fragments/SSH8.4.md`. `ItemWorkbench.cs` reads no
    materials path at all (the catalog is injected), recorded so nobody hunts a third reader.
  - ⏫ **RE-CHECKED 2026-09-22 by lane `ssh49f2`: still blocked on the SAME file.**
    `gk-core/tests/FusionRpg.Guard.Tests/TuningRevisionLiteralGuardTests.cs` carries no `materials.v{n}.json` rule
    (`grep -n Materials` there is empty), and that path is both pipeline-protected and outside lane
    `ssh49f2`'s allowed paths. `SocketTuningFiles.Materials` is already `materials.v6.json`, so the
    constant half is in. Dependency: the pipeline lane that owns the guard file. Re-check table:
    `tasks/reports/ssh49f2-blocked-rows-recheck.md`.

- [x] **SSH8.5 — Publish the derived bore / imbue / `forge-gem` souls coefficients as the next `materials` revision, only if the report is red (R12, R20)** · M · deps: SSH6.4, SSH8.4, species-gear-chain `T32` and `T34` (parent §5) · *(spec: socket-pricing §5)* · **parent H7**
  - Acceptance: `publish.py materials operations.bore.souls.coefficient=<derived> operations.imbue.souls.coefficient=<derived> operations.forge-gem.souls.coefficient=<derived>`, each key only where the report derived one and never below the derived value. Imbue legs = bore's + essence still holds. The materials constant → the new revision in the same commit
  - Acceptance: `combo-budget --report` exits 0 against the published prices; `a_gem_only_cell_is_fixed_by_the_derived_forge_gem_coefficient`; `a_cell_no_leg_can_move_is_named_not_published`. Provenance is then republished (SSH6.8, or a sockets re-publish if SSH6.8 has landed)
  - Acceptance: if SSH6.4 passed first time, the task closes as "not needed", with the report output as evidence
  - Verify: `cd tools\seedsmith; python -m seedsmith items combo-budget --report`; `dotnet test tests\FusionRpg.Core.Tests --filter "Category=BalanceGuard&FullyQualifiedName~ComboPricing|FullyQualifiedName~MaterialCorpus"`; `python gk-core/scripts/audit-magic-numbers.py --summary`; verify-change
  - Files: `data/tuning/materials.v{n}.json` (published), `gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs`, `tests/FusionRpg.Core.Tests/Items/ComboPricingTests.cs`
  - **DONE 2026-09-22 (lane `ssh29`) except ONE acceptance line, which is BLOCKED on SSH4.4.** Published
    `materials.v6.json` with the report's derived coefficients (`bore` 991, `imbue` 991, `forge-gem` 657)
    and switched every reader in the same commit (H7): `SocketTuningFiles.Materials`, `recipegen/brief.py`'s
    mirror, and the seven test literals. The report now reads **0 cells cheaper than the rarity route /
    126 unpriced** — every cell it can price passes. ⚠ **`combo-budget --report exits 0` does NOT pass:**
    exit 0 also requires zero REFUSED cells (`report/cli.py` returns `EXIT_GAP` on `failing or refused`),
    and the 126 unpriced cells are SSH4.4's owner-run corpus gap. Erratum requested (the line should
    read "0 failing cells, refusals attributed to SSH4.4", or the row waits for SSH4.4). Fixed here as
    well: `RequiredCoefficient` over-derived by ~1+c/1000 through an intermediate per-mille factor at a
    large coefficient — now one exact `CeilDiv`; and `ComboPricingBoot.cs:46`'s pre-existing
    magic-number M2 (`TierLadderRungCount = 1`) is resolved by reading the loaded ladder's count, not by
    allowlisting it (audit-magic-numbers TOTAL 0). Evidence: `tasks/evidence-fragments/SSH8.5.md`.
  - ✅ **CLOSED 2026-09-22 by lane `ssh49f2` — the last acceptance line now passes, so no erratum is
    needed.** SSH4.4 landed and the report is green at this HEAD: `cd gk-forge/tools/seedsmith; python -m seedsmith
    items combo-budget --report` -> exit 0, `PASS — every cell is at or under the rarity route (164 priced,
    0 refused)` — zero REFUSED cells, which is exactly what the line required. Re-check table:
    `tasks/reports/ssh49f2-blocked-rows-recheck.md`.

- [x] **SSH8.6 — `no_price_reads_the_actors_worn_combinations` (R12 source scan)** · XS · deps: SSH8.3 · *(spec: socket-pricing Testing, §5)*
  - Acceptance: the bore / imbue / insert cost paths take only the target item and the recipe. A scan of the workbench cost path finds no loadout, equipped-set or combination-count input
  - Verify: `dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~ComboCountCap"`; verify-change
  - Files: `gk-core/tests/FusionRpg.Guard.Tests/ComboCountCapGuardTests.cs`
  - **DONE 2026-09-22 (lane `ssh29`), in SSH6.5's guard file.** `no_price_reads_the_actors_worn_combinations`
    scans `gk-core/src/FusionRpg.Server/ItemWorkbench.cs` (the workbench cost path) for `Loadout` / `Equipped` /
    `EquippedBoundAtoms` / `CombinationResult` / `GetComboRecipes` / `ComboCount` (comments skipped) —
    **zero hits** — and asserts the ONE context builder every price goes through,
    `RecipeContextFor(long playerId, WorkbenchTarget t)`, still takes exactly TWO parameters, so a later
    edit cannot slip a loadout parameter in. `dotnet test tests\FusionRpg.Guard.Tests
    --filter "FullyQualifiedName~ComboCountCap"` → **2 passed / 0**. Evidence: `tasks/evidence-fragments/SSH8.6.md`.

### Checkpoint 6 — program exit (parent CC6)
- [ ] `strain-splice.v2.json` carries `tierLadder`, rung 1 equals the old floor, and the ladder was re-measured in the commit that published it
- [ ] No combination row carries `minTier`/`grantedTier`; the re-emit made no model call
- [ ] `socket-imbue` can be paid for every frame × concrete element; a mismatched essence is refused by name; a chaff chassis goes bore → imbue → fill → firing word through the real endpoints
- [ ] `combo-budget --report` exits 0 against the published materials revision; the provenance names it
- [ ] Full suite once (crosses Core/Data/Server/tool/seedsmith/tuning): `.\scripts\test-fast.ps1 -AllDefault`
- [ ] A live probe (RPG Server scope) on a real save: an imbued, laddered word on the real sheet (feeds parent CC8)

---

## Findings routed from `test-verification-boundary` (TVB5.7, 2026-09-20)

- [x] **SSH-F1 — the Core.Tests socket-word pin was not retired with the corpus** · SSH2.6
  (`e79c0fde8`) deleted `data/seed/items/socket-words/sockwords.json`, but
  `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:336`
  (`The_legacy_socket_word_corpus_is_ordered_and_awaits_module_21s_retirement`) still opened it, so it
  failed with `FileNotFoundException` and left the residual Core test project red. Repaired in the same
  commit as this row: the test is now
  `The_legacy_socket_word_corpus_is_retired_and_combination_is_the_only_kind`, asserting the file is
  gone and reading the retirement from `gk-data/packs/fusion/data/seed/items/socket-words/combogen-migrate.ledger.json`.
  Owning program: strain-splice-host.
  - ✅ **CLOSED 2026-09-22 (lane `ssh49f2`) — a fresh run, not a read.**
    `dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --nologo --filter "FullyQualifiedName~SocketOperationsTests"`
    -> `Failed: 0, Passed: 22, Skipped: 0, Total: 22`; and `gk-data/packs/fusion/data/seed/items/socket-words/` holds only
    `combogen-migrate.ledger.json`, so the absence the test asserts is real. ⚠ Two citations in this row
    are stale and are corrected here (they are also part of `SSH4.9-F6`): the file the Core.Tests split
    moved is `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs` (the retirement test is at
    `:336`), and its real name is `The_legacy_socket_word_corpus_is_retired_not_merely_unread`.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.
## Post-program corrections

- **SSH2.6's stale reader was FIXED (re-checked 2026-09-21 by lane `ssh28`; verified with a real run, not
  a read).** `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests"`
  → **22 passed / 0**; `gk-data/packs/fusion/data/seed/items/socket-words/` holds only `combogen-migrate.ledger.json`; and
  `KindCatalog.cs:140-149` records the removal through the verb. Evidence:
  `tasks/evidence-fragments/SSH2.6-lane-b.md` (a `No commit:` row — nothing needed changing).
  `SocketOperationsTests.The_legacy_socket_word_corpus_is_retired_not_merely_unread` now asserts the
  ABSENCE of the retired `sockwords.json` rather than reading it — `dotnet test
  gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests"` → **22 passed / 0**.
  The paragraph below is kept as history.
  ~~- **SSH2.6 left `SocketOperationsTests` red at HEAD (found 2026-09-20 by the cai-sink lane).**~~
  `gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs` (then `:340`) still reads
  the retired `socket-words` partition file (path no longer resolves), but `e79c0fde8` ("SSH2.6: retire socket-words for
  real", 2026-09-20) deleted that file (425 rows) and updated `KindCatalog.cs`, `combogen/migrate.py`
  and `metrics/linkage.py` — not this test, which was last touched by `12122abf`. The same commit
  leaves `No_shipped_gem_declares_an_omni_affinity` (`:329`) expecting `gem.g1-007` against an empty
  shipped-gem list. Cause read: SSH2.6's acceptance set is `KindCatalog` + `ItemSeedValidator` shaped
  and never runs `SocketOperationsTests`, so the stale test was invisible to it. Fix: retire the
  the retired `socket-words` reader (the corpus is deliberately absent) or re-point it at `combo.*`. Reproduce:
  `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~SocketOperationsTests"`.

- [x] **SSH5.10-P2 — four review notes from the independent H7 read of the `sockets.v2` flip** · XS ·
  *(filed by the manager, 2026-09-21; evidence `tasks/evidence-fragments/SSH5.10-independent-review.md`)*
  - The verdict was merge-OK (Q1–Q5 PASS, no reader defect). These are the notes it raised that are not
    reader defects but are the same drift class H7 polices.
  - (a) Stale prose naming v1 or the old ceiling 4: `SocketTuning.cs:55`, `StrainSpliceTuning.cs:14`,
    `RarityBudgetKeys.cs:59`, `gk-forge/tools/ItemSeedValidator/Checks/SocketMaxCheck.cs:11`,
    `gk-core/src/FusionRpg.Server/Program.cs:359-363` ("the structural 4" — now 8), `combogen/tuning.py:3,45`,
    `combogen/__init__.py:30`, `basetypegen/__init__.py:22`, `gemgen/__init__.py:6`.
  - (b) A **live-read** file names the superseded revision: `gk-core/data/tuning/strain-splice.v1.json:5,8,13`
    (still the live revision, `gk-core/src/FusionRpg.Server/Program.cs` — then `:374`) and `gk-core/data/tuning/base-types-gen.v1.json:9` `sourceRefs`
    point at `sockets.v1.json` for values that now live in v2.
  - (c) `gk-core/data/tuning/sockets.v2.json:3` carries `"version": 2` while `sockets.v1.json:3` carries
    `"version": 3` — non-monotonic (`gk-core/tools/tuning/publish.py:894-895` writes the filename-derived
    `v{n+1}`). No reader reads the field today; it is a trap for one that later does.
  - (d) Intentional, recorded so nobody "fixes" it: the corpus is not re-stamped, so
    `humanoid-head-guard-b.json` still tops out at `socketMax: 3` against v2's `head-guard: 4`, and
    `--retry-blocked` refuses that role by name until the owner-run SSH5.12.
  - Acceptance: (a)–(c) fixed or each explicitly declined with a reason on this row; (d) needs no change.
  - **DONE 2026-09-21 by lane `ssh28`.**
  - **(a) FIXED** — all ten sites re-worded to the current revision (`SocketTuningFiles.Current` in C#,
    "the current `sockets` revision" in the Python prose); revision-neutral wording, so the next publish
    cannot re-stale them. **Two more sites the review missed, same class**: `SocketTuning.cs:141`
    ("all ≤ 4" → `≤ StructuralCeiling`) and two stale TEST pins that were RED at the head —
    `BaseTypeSocketMaxCorpusTests` wrote `socketMax: 3` for `footing` (v1's ceiling 2; v2's is 4) and
    `CombinationImportTests` used `head-guard` to trigger `host-cannot-hold` (v2 lifts the helm to 4, so
    the row was ACCEPTED). Both now derive the role's ceiling from the loaded revision, so the contract
    is asserted without a revision literal. `FusionRpg.Server.Tests`: **758 passed / 0 failed** (was 756/2).
  - **(b) DECLINED, with the reason:** `gk-core/data/tuning/strain-splice.v1.json:5,8,13` and
    `gk-core/data/tuning/base-types-gen.v1.json:9` are PUBLISHED tuning files. Hand-editing them is forbidden
    (AGENTS.md; H7) and re-publishing is impossible — `gk-core/tools/tuning/publish.py` refuses to overwrite an
    existing revision. The strain-splice prose is rewritten by SSH7.7's `strain-splice.v2` publish
    (`--remove-key recipe:minTierPlan`, `--add-key recipe:tierLadder`), which is the same edit that must
    move the file; the `base-types-gen` `sourceRefs` entry moves with its own next publish. Neither is a
    lane's to patch in place, so no commit here changes them.
  - **(c) DECLINED, with the reason and the mitigation:** both files are immutable in place (same as (b)),
    so the historical wart (v1's field 3, v2's 2) cannot be corrected without republishing v1 or v2. The
    trap half is discharged: `grep` over `gk-core/src/FusionRpg.Core/Items/Sockets/*.cs` and
    `tools/seedsmith/.../combogen/tuning.py` for `"version"`/`schemaVersion` finds **no reader** of the
    field. `publish.py:894-895` derives the next value as `max(filename revision) + 1`, so the next
    publish (SSH6.8's `sockets` v3) writes `version: 3` and every later revision increases — monotonic
    from v2 onward; the v1/v2 pair is history.
  - **Evidence:** `tasks/evidence-fragments/SSH5.10-P2.md`.
  - Verify: `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`; `python -m pytest
    gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q`; for (c) a publish-mode check that the internal
    `version` field is not read by any loader.

### [ ] SSH-F1 `strain-splice-host` docs cite a line that no longer exists in the combogen emitter

- **Found:** 2026-09-21 by lane `tvb59` running `pwsh -NoProfile -File scripts/guard-doc-citations.ps1`
  (exit 1) while re-blessing TVB5.7. This program's own documents carry four D2 HIGH findings, and they are
  **new** at this head — `tasks/test-verification-boundary-todo.md`'s TVB-F15 names four other programs
  (notification-ssot, npc-story-events, trade-network, world-stage, legion-build) but not this one, so they
  were not covered by that row. The two documents are `docs/architecture/strain-splice-host-map.md` (two
  findings) and `docs/architecture/strain-splice-host/spec-tier-ladder.md` (two).
- **Cause read:** each of the four citations points at line 185 of the seedsmith combogen emitter, and that
  file is now 175 lines — the cited line was removed when the emitter shrank, so the citation can no longer
  be opened. The guard is gating in CI, so the whole-repo `doc-citations` guard stays red until it is
  re-anchored.
- **Remedy:** re-anchor the four citations to the current line of what they describe (or say on the line that
  the content moved), then `pwsh -NoProfile -File scripts/guard-doc-citations.ps1` exits 0 for these four.
- **Verify:** `python scripts/audit-doc-citations.py --strict --scope docs/architecture/strain-splice-host-map.md`
  and the same for `docs/architecture/strain-splice-host/spec-tier-ladder.md` → 0 HIGH.
## Findings routed from `combat-ai` (lane `combat-ai-3`, 2026-09-21)

Both are **CI-tier guard reds introduced by this program's commits**, found when lane `combat-ai-3`
merged `features/mega-merge` to `b79e28ff` and ran the two guards at the merged head. Neither is
`combat-ai`'s file and neither is in that lane's fence, so they are routed with the measured numbers
rather than fixed. They are gating in CI: `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci` cannot
be green while either is open.

- [x] **`SSH-route-1` — `guard-magic-numbers` M2 HIGH + M4 LOW at `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs:46`** ·XS ·
  deps: — · *(introduced with SSH6.x/7.x's combo-pricing boot, merged 2026-09-21)*
  `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` → exit 1, `M1=0  M2=1  M3=0  M4=1`, total 2
  findings (1 high), **both** on `public const int TierLadderRungCount = 1;`.
  - **Cause read, not guessed:** the const is passed as the third argument to
    `ComboPricingProvenance.Check` (`:56`), and its own doc comment says it *"is that row's marker, not a
    second source of truth"* — SSH7.1 (`tier-ladder`) is the row that publishes the rungs. So it is a
    **structural bridge carrying balance-sounding vocabulary**, which is exactly the ambiguity M2 exists
    to force a decision on. Two legitimate remedies, and this program's owner picks:
    (a) move the rung count into `gk-core/data/tuning` when SSH7.1 lands and have this read it (M2's own standard:
    no magic numbers on the balance surface, `docs/architecture/tunables-ssot.md`); or
    (b) show the guard's own structural-const justification, the precedent being `combat-ai`'s
    `DecisionScratchCapacity` (filed as that program's `CAI-guard-2`, fixed in `5fd0feba`).
    **Never** widen the audit's scan or add an exemption entry without naming the reason — M4's "tunable
    with no unit in its name" also disappears under either fix, because a real unit name (`RungCount`) is
    what (a) supplies.
  - Reproduce: `python gk-core/scripts/audit-magic-numbers.py --targets M2`; `python gk-core/scripts/audit-magic-numbers.py --targets M4`.
  - Verify: `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` green (`M1=0 M2=0 M3=0 M4=0`).
  - ✅ **CLOSED 2026-09-22 (lane `ssh49f2`) — the guard is green at this HEAD, fixed by SSH8.5's remedy.**
    `pwsh -NoProfile -File scripts/guard-magic-numbers.ps1` -> `M1=0  M2=0  M3=0  M4=0`, `total 0
    finding(s), 0 high`, `MAGIC-NUMBER GUARD OK`; `python gk-core/scripts/audit-magic-numbers.py --summary` ->
    `TOTAL 0 0 0 0 0`. The const is gone from the balance surface by remedy (a) in spirit: SSH8.5's note
    records that `TierLadderRungCount` is now read from the loaded ladder's count rather than declared as
    `= 1`, so no exemption entry was added and M4's "tunable with no unit in its name" disappears with it.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.

- [x] **`SSH-route-2` — `guard-population-pin` P1 at `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:70`** ·XS · deps: —
  `pwsh -NoProfile -File scripts/guard-population-pin.ps1` → exit 1, total 1 finding, on
  `Assert.Equal(64, loaded.CombinationCorpusDigest.Length);`.
  - **Cause read:** `64` is the **hex length of a SHA-256 digest**, not a content population — the guard
    flags it because the test file carries a `FindRepoRoot()`-style path helper, which is the content
    signal P1 keys on. The guard's own header is explicit about the remedy
    (`gk-core/scripts/guard-population-pin.py:13`): *"the fix is never a marker, it is rewriting the assertion as
    the contract."* So compare against the digest's own named length (the `ContentHash` hex-length constant,
    or `2 * SHA256.HashSizeInBytes`) with the why-comment, exactly as the sibling assertion one line above
    (`:69`) already does with `SocketLimits.SocketCircuitSize`. A `pin:` marker would be the wrong fix twice
    over: it hides a hash length behind population vocabulary.
  - Reproduce: `python gk-core/scripts/guard-population-pin.py --targets P1`.
  - Verify: `pwsh -NoProfile -File scripts/guard-population-pin.ps1` green (0 findings).
  - ✅ **CLOSED 2026-09-22 (lane `ssh49f2`) — the guard is green and the fix is the row's own remedy.**
    `pwsh -NoProfile -File scripts/guard-population-pin.ps1` -> `total 0 finding(s)`. The offending pin
    was rewritten AS THE CONTRACT, exactly as `gk-core/scripts/guard-population-pin.py` requires:
    `gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs:82` now reads
    `Assert.Equal(SHA256.HashSizeInBytes * 2, loaded.CombinationCorpusDigest.Length);` with the why-comment
    that a SHA-256 digest's WIDTH is a property of the algorithm (plus an `Uri.IsHexDigit` lower-case
    check eight lines below). No `pin:` marker was added.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.

- [x] **SSH-RED-1** (routed by notification-ssot, 2026-09-21) Two `FusionRpg.Server.Tests` reds sit at the
  merged head `287a3256`, both in test files this program's rows name, so the default suite cannot go
  green for CC8 until they do:
  - `CombinationImportTests.A_refused_recipe_is_never_seeded` (`gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs`)
  - `BaseTypeSocketMaxCorpusTests.A_base_row_above_its_role_ceiling_is_refused_at_load`
    (`gk-core/tests/FusionRpg.Server.Tests/BaseTypeSocketMaxCorpusTests.cs` — the class `data-test-substrate`'s T18d
    note deliberately left on a baseline, so the ceiling assertion may belong to that program instead)
  Reproduce: `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` -> `Failed! - Failed: 2, Passed: 761,
  Skipped: 0, Total: 763`. Filed here rather than left in another lane's report; route the second row to its
  real owner if that is not this program.
  - ✅ **CLOSED 2026-09-22 (lane `ssh49f2`) — both named tests pass at this HEAD.**
    `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --filter
    "FullyQualifiedName~CombinationImportTests|FullyQualifiedName~BaseTypeSocketMaxCorpusTests"` ->
    `Failed: 0, Passed: 7, Skipped: 0, Total: 7`; and the two methods by name (the row's own names, no
    class filter) -> `Passed ...A_refused_recipe_is_never_seeded`, `Passed
    ...A_base_row_above_its_role_ceiling_is_refused_at_load`, `Total tests: 2`. The `<287a3256` reading is
    history; the Release default suite is no longer blocked by these two.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.

---

## Finding routed from `test-verification-boundary` (TVB-F18, 2026-09-21)

- [ ] **TVB-F18 — two citations into `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` are stale after SSH7.3 shrank the file** ·
  `docs/architecture/strain-splice-host/spec-tier-ladder.md:19` and `:114` cite
  `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` (the cited line 185 is gone since SSH7.3), but that file is now **175 lines** (SSH7.3,
  `6efef718a`, removed `minTier`/`grantedTier` from the generator), so the citation is a past-end D2 — an
  `audit-doc-citations.py --strict` HIGH. Found while re-anchoring the Items-split citations in this program's
  own docs; the same two-citation pattern in `docs/architecture/strain-splice-host-map.md:46,119` was fixed in
  the TVB5.8.30 commit because that document was in that increment's scope. Fix is one line per citation: cite
  the file without the dead line number and say the cited lines are gone since SSH7.3. Owning program:
  strain-splice-host.
  - ⛔ **STILL BLOCKED 2026-09-22 — on this lane's FENCE, exactly one path.** The two citations to re-anchor are
    in `docs/architecture/strain-splice-host/spec-tier-ladder.md` (its `:19` and `:114`), and lane `ssh49f2`'s
    allowed paths carry `docs/architecture/item/**` only, not `docs/architecture/strain-splice-host/**`. The
    todo-side half of the same defect was fixed with `SSH4.9-F6` (this file's own `emit.py` citations now
    audit clean), so the remaining work is one line per citation in that one spec file — a lane with that
    path, or a fence widening.

- [x] **SSH4.9-P2 — the sanctioned item-grant route (owner ruling 2026-09-22)** · S · deps: SSH4.9-P1
  - Acceptance: an RPG Server Debug route that grants a real item (and the gem/material inputs a probe needs), minting nothing gameplay could not, with the changed state read back through the normal path
  - ✅ **DONE.** `POST /api/debug/grant-item` (shipped base type -> container upsert -> REAL `Instantiator` -> `SaveInstance`/`AcquireItem`/`ItemGenerationRow`), `POST /api/debug/grant-gem` (shipped gem -> `AdjustStock`), `POST /api/debug/grant-materials` (`AwardSouls` + `GrantMaterials`); all three scope-labelled and each returning the state read back from the store. Used by the live probe (4 bores + 4 inserts + equip, all 200). Evidence: `tasks/evidence-fragments/SSH4.9.md`.
  - ⚠ No unit test yet (exercised through the live endpoints only).

- [ ] **SSH4.9-P1 — INCIDENT: the first live-probe attempt deployed to the OWNER's install**     - *(Superseded: the row this replaced — "no sanctioned route can put a socketable item in a save" —
      is answered by the route above. Its measurements are kept because they are why the route exists: the
      catalog was never the problem — **1178 base types, 984 declaring `socketMax >= 1`** — while the save
      held four items and none socketable, and `GET /api/items/workbench/inserts/1` returned `[]`. Owner
      question answered 2026-09-22: build the route.)*
· S · *(self-reported by lane `ssh29` 2026-09-22, contained by the lane, guard added by the manager)*
  - **What happened:** a bash `export FUSIONRPG_GAME_DIR=<slot>` did not reach `deploy-play.ps1`, whose MelonLoader branch **defaults to the owner's install** (`H:\Games\PVZ-Fusion-3.9_MelonLoader`) when `FUSIONRPG_ML_GAMEDIR` is unset. So the deploy wrote `Mods/fusionrpg.cfg` there, refreshed the injector, and launched the owner's game against the owner's server `127.0.0.1:5088`.
  - **Containment (the lane's own):** killed only the PID it launched (verified gone), released slot 1 (pool back to 3/3 free), no further deploy. The owner's **server** was untouched — verified running and listening on `:5088` afterwards.
  - **Damage, stated rather than smoothed over:** the previous `Mods/fusionrpg.cfg` content is **not restorable**; the owner's install also received an injector refresh. Nothing else was written.
  - **Root cause, as the lane diagnosed it:** an env var set by a prior `export` line does not reach the child `pwsh` invocation — it must be set **inline** (`VAR=... pwsh ...`) or the deploy falls back.
  - **The fix that makes the fallback impossible (manager, `scripts/deploy-play.ps1`):** when `FUSIONRPG_GAME_POOL` is set, the target MUST be inside the pool root or the script **refuses** (exit 3) with the reason. Verified: with the pool set and the target at the owner's install, it refuses; a pooled run can no longer default into the owner's install.
  - **Still owed:** SSH4.9 itself is **NOT RUN** — the probe must be re-attempted with the pool env inline, against a slot, after the lane merges this guard.
  - ⛔ **STILL BLOCKED 2026-09-22 — on the live probe, which is the manager's/owner's, not a lane's.** Every
    code-side prerequisite of SSH4.9 is done (SSH4.4, SSH4.6, SSH4.7, SSH4.8 and this lane's SSH4.9-F2
    re-measurement, whose E2E proof now shows the word firing and binding through the real routes); what
    this row still needs is a real running game + slot with the pool env set inline, which no agent here may
    start. The incident's own containment/guard work is complete.

- [x] **SSH4.9-F2 — RE-MEASURED 2026-09-22 by lane `ssh49f2`: NOT a defect — the mint and the read path key on the same corpus id, and a socketed gem fires** · S · deps: — · *(raised 2026-09-22 by lane `ssh29`, refuted by lane `ssh49f2`)*
  - **What the original finding claimed.** `socket-insert` stores a socket row whose `insert_container_id` is the minted, NAME-derived container (`gem.sturdy-layering`, `gem.bulwark-core` — read off the card's `insertKey`) while the read path resolves through the SHIPPED gem corpus by that id, so the fill contributes no combinable family and `GET /api/items/{id}/combinations` returns `[]`.
  - **What is actually true (measured, not inferred).** The socket row holds the corpus id it was inserted from. Driven through the real routes on the in-process `RpgApiFactory` host (grant-item -> 4x socket-add -> 4x socket-insert), `_store.GetSockets` reads back `gem.g2-002`, `gem.g1-023`, `gem.g3-009`, `gem.g1-019` — the ids, never their `nameKey`s. `gem.sturdy-layering` is `gem.g1-023`'s **`nameKey` display key**: `ssot-presentation.md` §2.4 ("atom ids, family ids, container ids, instance ids. Debug surfaces only.") is exactly why the card carries `insertKey` instead of the container id (`ItemCard.cs:552`). A filled socket the corpus does NOT carry cannot render at all — `RpgStore.ItemCard.cs:448` throws and `ItemCardEndpoints.cs:631` answers `409 item.card-unrenderable` — so the probe's 200 card is itself the proof the lookup HIT. Both sides key on the corpus `id`: mint `GemContainerBuild.cs:67`, row `SocketOperations.cs:102`, def `ItemCardEndpoints.cs:179`, read `ItemSurfaceEndpoints.cs:240`, equip `RpgStore.EquipCombinations.cs:96`. **No production line changes; the responsible layer was the reading.**
  - **Why the word did not fire — two product rules, both by design.** (1) `item.humanoid-torso-a-005` is a member of **8 shipped sets**, so `SocketHostFor` reports `IsSetPiece: true` and D21 (`SetExclusivityValidator.MayFire`, applied at `CombinationEvaluator.cs:79` / `CombinationDistance.cs:191`) withholds every Strain/Splice. (2) `combo.splice-agility-bulwark` declares `hostFrame: "plant"` and the chassis is `humanoid` — `ComboMatcher.HostAdmits` (`ComboMatcher.cs:73`) refuses it before the multiset is read. `/combinations` answered `[]` because an Active row is the only row `CompendiumReveal.Render` shows once the four gems have been spent out of stock.
  - **Regression proof (new).** `gk-core/tests/FusionRpg.E2E.Tests/SocketedGemCombinationE2ETests.cs`: on a non-set-piece `core-guard`/`humanoid` chassis (`item.humanoid-torso-b-001`) filled with the four shipped gems of `combo.splice-vigor-bulwark`, `/api/items/{id}/combinations` reads `state: "Active"`, `ComboTargetsFor` yields `cmb:{chassis}#c0:combo.splice-vigor-bulwark-t1`, and after a real `/api/items/equip` that binding is present in `ResolveBindings`; the probe's own set-piece chassis fires no splice and yields no target. Evidence: `tasks/reports/ssh49f2-socketed-gem-readback.md`.
  - **Not a ruling question any more** — there is no disagreement to rule on. The probe method correction (a card `insertKey` is a display key, never the stored container id) is recorded in the report above.

- [ ] **SSH4.9-F3 — `gk-data/packs/fusion/data/seed/rarity/**` has no copy rule, so a boot-seeded install has an EMPTY rarity ladder** · S · deps: — · *(found 2026-09-22 by lane `ssh49f2`)*
  - **Cause, read at `file:line`.** `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` copies `gk-core/data/tuning/**`, `gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/seed/atoms/**`, `gk-data/packs/fusion/data/seed/dungeon/**`, `gk-data/packs/fusion/data/seed/structures/**`, `gk-data/packs/fusion/data/seed/actions/*.json`, `gk-data/packs/fusion/data/seed/loot/*.json`, `gk-data/packs/fusion/data/seed/power/*.json`, `gk-data/packs/fusion/data/seed/commanders/**`, `gk-data/packs/fusion/data/seed/saves/**` — and **not** `gk-data/packs/fusion/data/seed/rarity/**`, one of `SeedScanner.AtomFolders` (`gk-core/src/FusionRpg.Data/Seed/SeedScanner.cs:46`). `SeedImportRunner.FindUp` (`gk-core/src/FusionRpg.Data/Seed/SeedImportRunner.cs:69-79`) walks UP from the exe and stops at the first directory that has `gk-data/packs/fusion/data/seed` — the exe's own partial copy — so the ladder file is never swept.
  - **Measured.** In the in-process E2E host the boot log prints `the rarity ladder has no seeded rows`, `RarityLadder`-dependent code sees zero rows, and `/api/debug/grant-item` dies with `System.InvalidOperationException: Sequence contains no elements` at its `rungs.First()` fallback (`gk-core/src/FusionRpg.Server/DebugEndpoints.cs:1347-1348`). The E2E test added by this lane must `UpsertRarity`/`SeedRarityLadder` by hand to get a rung.
  - **Why production has not noticed.** `scripts/deploy-play.ps1:412` runs `gk-forge/tools/AtomImporter --db <dist>/data` over the whole `gk-data/packs/fusion/data/seed` tree before the server starts, so the ladder lands in SQLite by a path the copy rule does not govern. A player/published install that relies on the server's own boot sweep (or any consumer of `gk-data/packs/fusion/data/seed/rarity`) has no ladder.
  - **Owning program:** unresolved — the copy rule is deployment/packaging (no program map row names it). Route to whoever owns `FusionRpg.Server.csproj`'s content rules. Not fixed here: the csproj is outside this lane's fence.
  - ⛔ **STILL BLOCKED 2026-09-22 — on this lane's FENCE, exactly one path.**
    `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` is the one file that carries the missing copy rule, and it
    is outside lane `ssh49f2`'s allowed paths (`gk-core/src/FusionRpg.Server/DebugEndpoints.cs` is the only file
    allowed under that project). One `<Content Include>` block for `data\seed\rarity\**\*.json` fixes it.

- [ ] **SSH4.9-F4 — a shipped base type names implicit family `atom.regeneration`, which no shipped atom row carries** · S · deps: — · *(found 2026-09-22 by lane `ssh49f2`)*
  - **Cause, read at `file:line`.** `gk-data/packs/fusion/data/seed/items/base-types/plant-core-guard-a.json:106,182,259` author `"family": "atom.regeneration"` for `item.plant-stem-a-005` (and siblings), and `/api/debug/grant-item` resolves that implicit family through `AtomRow.DeriveId(shipped.Family, "", 1)` + `store.GetAtom` (`gk-core/src/FusionRpg.Server/DebugEndpoints.cs:1339-1341`). No atom row carries the family: `grep -rn atom.regeneration gk-data/packs/fusion/data/seed/atoms/` is empty (the generated `family-expand.*.json` tree does not emit it), so the route answers `409 {"error":"the base type's implicit atom 'atom.regeneration.t1' is not in the loaded atom catalog"}`.
  - **Owning program:** unresolved — either the atom generator (`FamilyExpandGen`, `gk-data/packs/fusion/data/seed/atoms/generated/**`) owes the family, or the base-type corpus names a family nothing authors. Route to the owning content program. Not fixed here: `tools/` and the generated trees are outside this lane's fence.
  - ⛔ **STILL BLOCKED 2026-09-22 — on this lane's FENCE, and on a generator decision.** The fix is either a
    `gk-forge/tools/FamilyExpandGen` change plus a regeneration of `gk-data/packs/fusion/data/seed/atoms/generated/**`, or a
    `gk-data/packs/fusion/data/seed/items/base-types/**` correction — both outside lane `ssh49f2`'s allowed paths, and both the
    kind of edit the generated-data rule forbids by hand. Note this is the SAME family gap that makes the
    shipped `item.plant-stem-*` chassis unusable for a socket probe, which is why the SSH4.9-F2 regression
    test uses a `humanoid` chassis.

- [x] **SSH4.9-F5 — `/api/test/reset` did not clear `rpg_material_spend_log`, so two tests sharing a correlation id replayed each other** · S · deps: — · *(found 2026-09-22 by lane `ssh49f2`; fixed the same day when the fence grew to `gk-core/src/FusionRpg.Data/**`)*
  - **Cause, read at `file:line`.** `ItemWorkbench.Replay` (`gk-core/src/FusionRpg.Server/ItemWorkbench.cs:1543-1571`) answers from `_store.FindMaterialSpend(playerId, correlationId)`, and the E2E collection shares one `RpgApiFactory`/DB across test classes while `/api/test/reset` leaves the spend log standing. A second test that reuses a deterministic correlation id gets `replayed: true` and the FIRST test's instance in its socket list (measured: `bore 0 answered 200 with 0 rows ... "replayed":true, "instanceId":"6448b92c..."` for a chassis the caller had just been granted as `eb04a713...`).
  - **Owning program:** test substrate (`docs/contributing/testing-standard.md` territory). Either `/api/test/reset` clears the spend log or test correlation ids must be unique per test. Not fixed here: the reset route and the test helper are outside this lane's fence (the new test sidesteps it with a per-test correlation namespace).
  - ✅ **FIXED 2026-09-22 (lane `ssh49f2`) — the reset clears the ledger, and a test proves both halves.**
    `RpgStore.Reset()` now carries `DELETE FROM rpg_material_spend_log;` beside the souls and materials
    it already cleared, with the why-comment naming the replay lie. Reproduced BEFORE the fix and green
    after, both through the real routes on the in-process host:
    `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --filter "FullyQualifiedName~A_reset_clears_the_spend_ledger"`
    -> pre-fix **FAIL**, `correlation '...' was replayed after a reset: {"ok":true,...,"reason":"replay","instanceId":"01c94985...","replayed":true,"outcome":"replay",...}` — the 200 named the FIRST chassis; post-fix
    **`Passed! - Failed: 0, Passed: 1`**. The test is
    `tests/FusionRpg.E2E.Tests/SocketedGemCombinationE2ETests.A_reset_clears_the_spend_ledger_so_a_correlation_id_is_not_replayed`:
    two real chassis, one correlation id, one `/api/test/reset` between them, asserting
    `replayed == false` and that the outcome names the SECOND chassis. Full E2E suite with the fix:
    `Failed: 1, Passed: 236, Skipped: 0, Total: 237` — the one failure is the unrelated, pre-existing
    `RpgScenarioSlice0E2ETests` XP-ledger flake (recorded separately), not this change.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.

- [x] **SSH4.9-F6 — `verify-change.ps1` could not pass on THIS file: 13 D3 + 1 D2 doc-citation HIGHs were pre-existing in it** · S · deps: — · *(found 2026-09-22 by lane `ssh49f2`)*
  - **Cause, read at `file:line`.** `scripts/verify-change.ps1:247-250` runs `python scripts/audit-doc-citations.py --strict --scope <each changed markdown path>` and `:322` exits on its non-zero verdict, before the guards and tests run. `--scope tasks/strain-splice-host-todo.md` reports **14** HIGHs — 13 D3 bare-basename citations (`run.py`, `Program.cs`, `emit.py`, and two `SocketOperationsTests.cs` paths the Core.Tests split moved) plus one D2 for the `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/emit.py` citation that SSH7.3 left stale (the file is 175 lines). So **every** lane whose task requires a row in this todo is blocked from the standard verification until they are re-anchored. (Deliberately no line numbers here: they shift with every edit above them, which is the trap this row is about.)
  - **Proof they are pre-existing, not this lane's.** The lane's only diff hunk in this file starts at line 989 (`git diff -U0 tasks/strain-splice-host-todo.md` -> `@@ -989,5 +989,20 @@`), so every audited line is byte-identical to HEAD. Two of them are TVB-F18's own open row (above).
  - **Owning program:** strain-splice-host (the file is this program's todo). Re-anchoring is citation archaeology across other lanes' rows — the `run.py` / `Program.cs` / `emit.py` rows name their tool only in prose, and the two Core.Tests paths need the post-split location — so it is filed rather than guessed at. Reported as `fail` on the `verify-change.ps1` acceptance; the achievable checks (E2E suite, `guard-test-substrate`, `session-boundary-check`) all ran green.
  - ✅ **CLOSED 2026-09-22 (lane `ssh49f2`) — all 14 re-anchored, and the file audits clean.**
    `python scripts/audit-doc-citations.py --strict --scope tasks/strain-splice-host-todo.md` ->
    `372 resolvable citations checked`, `D1 0 / D2 0 / D3 0 / D4 0`, **exit 0**. The fixes, one per
    finding: the two `SocketOperationsTests` paths now name the post-split project
    (`gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:336` for the live test, and the
    historical paragraph in SSH-F1's row cites it line-less with "(then `:340`)"); the six bare
    `run.py` line references in SSH2.9's row now carry the full
    `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/run.py` path for the NEW line numbers and express
    the OLD ones as prose ("line 79 -> 80") so no citation points at a line that moved; `deps.py`'s two
    references are line-less on the same grounds; SSH5.10-P2's bare Program.cs reference now names
    `gk-core/src/FusionRpg.Server/Program.cs` with "(then `:374`)"; and the past-end emit.py line — which is
    beyond the file's 175 lines — is cited as the full path with the line's disappearance stated on the
    line, in both the SSH2.9 note and TVB-F18's own row. No audit exemption was added and no scan was widened, which the audit
    proves by still reporting D2/D3 as codes.
    Reading: `tasks/reports/ssh49f2-open-rows-readings.md`.

- [ ] **SSH-F7 — `RpgScenarioSlice0E2ETests` fails roughly half of full E2E runs on an XP-ledger `runId` read-back (pre-existing, shared-factory)** · S · deps: — · *(found 2026-09-22 by lane `ssh49f2` while landing SSH4.9-F5; not this program's code defect, but this program's E2E substrate)*
  - **Symptom, printed.** `Assert.Contains() Failure: Filter not matched in collection` on the XP-ledger read-back in `gk-core/tests/FusionRpg.E2E.Tests/RpgScenarioSlice0E2ETests.cs` — the `Assert.All(xpRows, row => Assert.Contains(row.GetProperty("runId").GetInt64(), ctx.BattleRunIds))` line. The printed collection is the player's whole XP ledger: `{"id":12,"runId":1,"delta":25,"reason":"defeat","refKind":"activity_fact","refId":"8"}`, `{"id":11,"runId":0,"delta":500,"reason":"discovery","refKind":"species","refId":"solarsunflower"}`, `...` — i.e. a `runId: 0` discovery row sits beside the battle rows.
  - **Readings (all measured by this lane).** Debug suite with the new socketed-gem class: `Failed: 1, Passed: 236, Skipped: 0, Total: 237` — measured BOTH before and after SSH4.9-F5's fix, so that fix is not the trigger. Release suite: `Failed: 1, Passed: 235` twice, once this test and once `CatalogAndStressE2ETests.Enqueue_2000_returns_fast_then_persists` (a 100 ms wall-clock budget; printed `enqueue ms 102`). The scenario test passes ALONE (`Total tests: 1`) and as a pair with the socketed-gem class (`Failed: 0, Passed: 3`); the Release suite with the socketed-gem class filtered out is `Passed! 234/234`.
  - **The cause is NOT yet read, and that is stated rather than guessed.** The two facts established are that the ledger contains `runId: 0` discovery rows beside the battle rows, and that the assertion requires EVERY row's `runId` to be among the run ids the expedition's `collect` response returned. Whether a `collect` can return run id 0 (i.e. whether the sequence position after `/api/test/reset`, which clears `sqlite_sequence`) decides this is the open question. Next step: read the XP-ledger writer and the scenario's own collect response — never widen the assertion.
  - **Owning program:** strain-splice-host (the file is this program's E2E substrate). The file IS in lane `ssh49f2`'s fence; it is filed rather than patched because patching an assertion whose contract has not been read is the class of change this repo's guard rules exist to prevent.
